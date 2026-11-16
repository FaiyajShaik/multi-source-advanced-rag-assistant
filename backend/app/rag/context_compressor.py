
import re

from app.rag.embeddings import generate_embedding


def split_sentences(text: str) -> list[str]:
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def compress_context(
    documents: list[dict],
    question: str,
    max_characters: int = 3000,
    relevance_threshold: float = 0.78,
    fallback_top_k: int = 2,
    max_sentences: int = 10,
):
    if not documents:
        return []

    question_embedding = generate_embedding(question)

    candidates = []

    # Calculate relevance scores for every sentence.
    for document_index, document in enumerate(documents):

        sentences = split_sentences(
            document["text"]
        )

        for sentence_index, sentence in enumerate(sentences):

            sentence_embedding = generate_embedding(
                sentence
            )

            relevance_score = cosine_similarity(
                question_embedding,
                sentence_embedding,
            )

            candidates.append({
                **document,
                "text": sentence,
                "compression_score": relevance_score,
                "_document_index": document_index,
                "_sentence_index": sentence_index,
            })

    # Rank sentences by relevance.
    candidates.sort(
        key=lambda item: item["compression_score"],
        reverse=True,
    )

    # Select sentences that meet the relevance threshold.
    relevant_candidates = [
        candidate
        for candidate in candidates
        if candidate["compression_score"] >= relevance_threshold
    ]

    print("\n===== CONTEXT COMPRESSION SCORES =====")

    for candidate in candidates[:10]:
        print(
            f"Score: {candidate['compression_score']:.4f} | "
            f"Selected: {candidate['compression_score'] >= relevance_threshold} | "
            f"Text: {candidate['text'][:150]}"
        )

    print("Sentences after threshold:", len(relevant_candidates))
    print("Total sentences:", len(candidates))

    # Fallback: retain the highest-scoring sentences
    # when none meet the relevance threshold.
    if not relevant_candidates and candidates:
        relevant_candidates = candidates[:fallback_top_k]

    # Limit the total number of selected sentences.
    relevant_candidates = relevant_candidates[:max_sentences]

    # Restore the original document and sentence order.
    relevant_candidates.sort(
        key=lambda item: (
            item["_document_index"],
            item["_sentence_index"],
        )
    )

    # Group selected sentences by their original chunk ID.
    grouped_documents = {}

    for candidate in relevant_candidates:

        document_key = (
            candidate.get("chunk_id")
            or f"{candidate.get('source')}::{candidate['_document_index']}"
        )

        if document_key not in grouped_documents:
            grouped_documents[document_key] = {
                **candidate,
                "text": "",
            }

        grouped_documents[document_key]["text"] += (
            candidate["text"] + " "
        )

    # Build the final compressed documents.
    compressed_documents = []
    total_characters = 0

    for document in grouped_documents.values():

        document["text"] = document["text"].strip()

        if total_characters + len(document["text"]) > max_characters:
            continue

        # Remove internal sentence-order metadata.
        document.pop("_document_index", None)
        document.pop("_sentence_index", None)

        compressed_documents.append(document)
        total_characters += len(document["text"])

    print("\n===== FINAL COMPRESSION SUMMARY =====")
    print("Compressed documents:", len(compressed_documents))
    print("Total characters:", total_characters)

    return compressed_documents
