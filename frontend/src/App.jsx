
import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'

import {
  askQuestion,
  uploadDocuments,
  ingestWebsite,
  getKnowledgeBaseDocuments,
  getUploadedDocuments,
  getIndexedWebsites,
  refreshTemporaryData,
} from './services/api'

import './App.css'


const KNOWLEDGE_BASE_DETAILS = {
  'test.txt': {
    title: 'Employee Policies',
    description:
      'Information about employee leave, remote work, working hours, benefits, and expense reimbursement.',
    examples: [
      'How many paid leave days are available?',
      'What is the remote work policy?',
      'What are the standard working hours?',
      'How do I claim business expenses?',
    ],
  },
  'test_second.txt': {
    title: 'Employee Travel Policy',
    description:
      'Information about manager approval for business travel and reimbursement of travel expenses.',
    examples: [
      'Is manager approval required before booking travel?',
      'What receipts are required for reimbursement?',
    ],
  },
  'test_policy.pdf': {
    title: 'Employee Benefits Policy',
    description:
      'Information about health insurance eligibility and contacting Human Resources for benefits questions.',
    examples: [
      'When do employees become eligible for health insurance?',
      'Who should I contact about benefits?',
    ],
  },
  'test_policy.docx': {
    title: 'Employee Travel Policy',
    description:
      'Information about manager approval before business travel and valid receipts for travel expenses.',
    examples: [
      'Do I need manager approval for business travel?',
      'What documents are required for travel expenses?',
    ],
  },
}


function App() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [sourceType, setSourceType] = useState('')

  const [knowledgeBaseDocuments, setKnowledgeBaseDocuments] = useState([])
  const [selectedKnowledgeBaseIds, setSelectedKnowledgeBaseIds] = useState([])
  const [confirmedKnowledgeBaseIds, setConfirmedKnowledgeBaseIds] = useState([])
  const [knowledgeBaseLoading, setKnowledgeBaseLoading] = useState(false)
  const [knowledgeBaseError, setKnowledgeBaseError] = useState('')

  const [uploadedDocuments, setUploadedDocuments] = useState([])
  const [selectedUploadIds, setSelectedUploadIds] = useState([])
  const [confirmedUploadIds, setConfirmedUploadIds] = useState([])
  const [uploadListLoading, setUploadListLoading] = useState(false)
  const [uploadListError, setUploadListError] = useState('')

  const [websites, setWebsites] = useState([])
  const [selectedWebsiteIds, setSelectedWebsiteIds] = useState([])
  const [confirmedWebsiteIds, setConfirmedWebsiteIds] = useState([])
  const [websiteLoading, setWebsiteLoading] = useState(false)
  const [websiteListError, setWebsiteListError] = useState('')

  const [selectedFiles, setSelectedFiles] = useState([])
  const [websiteUrl, setWebsiteUrl] = useState('')

  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const [error, setError] = useState('')
  const [ingestionMessage, setIngestionMessage] = useState('')
  const [ingestionError, setIngestionError] = useState('')

  const fileInputRef = useRef(null)


  function resetConversation() {
    setQuestion('')
    setAnswer('')
    setSources([])
    setError('')
  }


  async function loadKnowledgeBase() {
    setKnowledgeBaseLoading(true)
    setKnowledgeBaseError('')

    try {
      const result = await getKnowledgeBaseDocuments()
      const documents = Array.isArray(result.documents)
        ? result.documents
        : []

      setKnowledgeBaseDocuments(documents)
      setSelectedKnowledgeBaseIds(
        documents.map((document) => document.document_id)
      )
      setConfirmedKnowledgeBaseIds([])
    } catch (err) {
      setKnowledgeBaseError(err.message)
    } finally {
      setKnowledgeBaseLoading(false)
    }
  }


  async function loadUploads() {
    setUploadListLoading(true)
    setUploadListError('')

    try {
      const result = await getUploadedDocuments()
      const documents = Array.isArray(result.documents)
        ? result.documents
        : []

      setUploadedDocuments(documents)
      setSelectedUploadIds(
        documents.map((document) => document.document_id)
      )
      setConfirmedUploadIds([])
    } catch (err) {
      setUploadListError(err.message)
    } finally {
      setUploadListLoading(false)
    }
  }


  async function loadWebsites() {
    setWebsiteLoading(true)
    setWebsiteListError('')

    try {
      const result = await getIndexedWebsites()
      const websiteList = Array.isArray(result.websites)
        ? result.websites
        : []

      setWebsites(websiteList)
      setSelectedWebsiteIds(
        websiteList.map((website) => website.document_id)
      )
      setConfirmedWebsiteIds([])
    } catch (err) {
      setWebsiteListError(err.message)
    } finally {
      setWebsiteLoading(false)
    }
  }


  async function loadAllSources() {
    await Promise.all([
      loadKnowledgeBase(),
      loadUploads(),
      loadWebsites(),
    ])
  }


  useEffect(() => {
    if (sourceType === 'knowledge_base') {
      loadKnowledgeBase()
    }

    if (sourceType === 'upload') {
      loadUploads()
    }

    if (sourceType === 'website') {
      loadWebsites()
    }

    if (sourceType === 'all') {
      loadAllSources()
    }
  }, [sourceType])


  function handleSourceChange(event) {
    setSourceType(event.target.value)
    resetConversation()

    setIngestionMessage('')
    setIngestionError('')

    setConfirmedKnowledgeBaseIds([])
    setConfirmedUploadIds([])
    setConfirmedWebsiteIds([])
  }


  function toggleId(id, selectedIds, setSelectedIds, setConfirmedIds) {
    setSelectedIds((previous) =>
      previous.includes(id)
        ? previous.filter((item) => item !== id)
        : [...previous, id]
    )

    setConfirmedIds([])
  }


  function handleSelectAll(ids, setSelectedIds, setConfirmedIds) {
    setSelectedIds([...ids])
    setConfirmedIds([])
  }


  function handleDeselectAll(setSelectedIds, setConfirmedIds) {
    setSelectedIds([])
    setConfirmedIds([])
  }


  function handleContinue(selectedIds, setConfirmedIds) {
    if (!selectedIds.length) return

    setConfirmedIds([...selectedIds])
    resetConversation()
  }


  async function handleUpload(event) {
    event.preventDefault()

    if (!selectedFiles.length || uploading) return

    setUploading(true)
    setIngestionMessage('')
    setIngestionError('')

    try {
      const result = await uploadDocuments(selectedFiles)

      const successful = result.successful_count || 0
      const failed = result.failed_count || 0

      setIngestionMessage(
        `${successful} document(s) uploaded successfully. ${failed} failed.`
      )

      if (result.failures?.length) {
        setIngestionError(
          result.failures
            .map((item) => `${item.filename}: ${item.error}`)
            .join('\n')
        )
      }

      setSelectedFiles([])

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      if (sourceType === 'all') {
        await loadAllSources()
      } else {
        await loadUploads()
      }

      resetConversation()
    } catch (err) {
      setIngestionError(err.message || 'Document upload failed.')
    } finally {
      setUploading(false)
    }
  }


  async function handleWebsiteIngestion(event) {
    event.preventDefault()

    const url = websiteUrl.trim()

    if (!url || ingesting) return

    setIngesting(true)
    setIngestionMessage('')
    setIngestionError('')

    try {
      const result = await ingestWebsite(url)

      setWebsiteUrl('')

      setIngestionMessage(
        `Website indexed successfully. ${result.chunks_indexed} chunks indexed.`
      )

      if (sourceType === 'all') {
        await loadAllSources()
      } else {
        await loadWebsites()
      }

      resetConversation()
    } catch (err) {
      setIngestionError(err.message || 'Website ingestion failed.')
    } finally {
      setIngesting(false)
    }
  }


  async function handleRefresh() {
    if (refreshing || loading) return

    const confirmed = window.confirm(
      'Refresh removes all uploaded documents and websites. Your permanent Knowledge Base will be preserved. Continue?'
    )

    if (!confirmed) return

    setRefreshing(true)
    setIngestionMessage('')
    setIngestionError('')

    try {
      await refreshTemporaryData()

      setUploadedDocuments([])
      setSelectedUploadIds([])
      setConfirmedUploadIds([])

      setWebsites([])
      setSelectedWebsiteIds([])
      setConfirmedWebsiteIds([])

      setSelectedFiles([])

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      setIngestionMessage(
        'Uploaded documents and websites have been removed. Your permanent Knowledge Base was preserved.'
      )

      resetConversation()
    } catch (err) {
      setIngestionError(err.message || 'Refresh failed.')
    } finally {
      setRefreshing(false)
    }
  }


  async function handleSubmit(event) {
    event.preventDefault()

    const trimmedQuestion = question.trim()

    if (!trimmedQuestion || loading) return

    let documentIds = null

    if (sourceType === 'knowledge_base') {
      documentIds = confirmedKnowledgeBaseIds
    } else if (sourceType === 'upload') {
      documentIds = confirmedUploadIds
    } else if (sourceType === 'website') {
      documentIds = confirmedWebsiteIds
    } else if (sourceType === 'all') {
      documentIds = [
        ...selectedKnowledgeBaseIds,
        ...selectedUploadIds,
        ...selectedWebsiteIds,
      ]
    }

    if (!documentIds || documentIds.length === 0) {
      setError('Please select at least one source.')
      return
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const result = await askQuestion(
        trimmedQuestion,
        sourceType,
        documentIds
      )

      if (!result || typeof result.answer !== 'string') {
        throw new Error('The server returned an invalid response.')
      }

      setAnswer(result.answer)
      setSources(Array.isArray(result.sources) ? result.sources : [])
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }


  const groupedSources = Object.values(
    sources.reduce((groups, source) => {
      const key = `${source.source_type}::${source.source}`

      if (!groups[key]) {
        groups[key] = { ...source, chunks: [] }
      }

      if (source.text) {
        groups[key].chunks.push(source.text)
      }

      return groups
    }, {})
  )


  const sourceReady =
    sourceType === 'all' ||
    (sourceType === 'knowledge_base' && confirmedKnowledgeBaseIds.length > 0) ||
    (sourceType === 'upload' && confirmedUploadIds.length > 0) ||
    (sourceType === 'website' && confirmedWebsiteIds.length > 0)


  const hasConversation =
    question || answer || sources.length > 0 || error


  function renderKnowledgeBaseList() {
    return (
      <section className="knowledge-base-section">
        <h2>Permanent Knowledge Base</h2>

        <p>
          These documents are permanent. Select the documents you want to search.
        </p>

        {knowledgeBaseLoading && (
          <div className="loading-message">Loading Knowledge Base...</div>
        )}

        {knowledgeBaseError && (
          <div className="error-message">{knowledgeBaseError}</div>
        )}

        {!knowledgeBaseLoading && knowledgeBaseDocuments.length === 0 && (
          <p>No Knowledge Base documents found.</p>
        )}

        {knowledgeBaseDocuments.length > 0 && (
          <>
            <div className="knowledge-base-actions">
              <p>
                {selectedKnowledgeBaseIds.length} of {knowledgeBaseDocuments.length} selected
              </p>

              <div>
                <button
                  type="button"
                  onClick={() =>
                    handleSelectAll(
                      knowledgeBaseDocuments.map((doc) => doc.document_id),
                      setSelectedKnowledgeBaseIds,
                      setConfirmedKnowledgeBaseIds
                    )
                  }
                >
                  Select All
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleDeselectAll(
                      setSelectedKnowledgeBaseIds,
                      setConfirmedKnowledgeBaseIds
                    )
                  }
                >
                  Deselect All
                </button>
              </div>
            </div>

            <div className="knowledge-base-list">
              {knowledgeBaseDocuments.map((document) => {
                const details = KNOWLEDGE_BASE_DETAILS[document.filename] || {
                  title: document.filename,
                  description: 'Explore this indexed document.',
                  examples: [],
                }

                return (
                  <article
                    className="knowledge-base-card"
                    key={document.document_id}
                  >
                    <div className="knowledge-base-card-header">
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedKnowledgeBaseIds.includes(document.document_id)}
                          onChange={() =>
                            toggleId(
                              document.document_id,
                              selectedKnowledgeBaseIds,
                              setSelectedKnowledgeBaseIds,
                              setConfirmedKnowledgeBaseIds
                            )
                          }
                        />
                        <span>{details.title}</span>
                      </label>

                      <span className="document-filename">
                        {document.filename}
                      </span>
                    </div>

                    <p>{details.description}</p>

                    {details.examples.length > 0 && (
                      <div className="example-questions">
                        <strong>Example questions</strong>
                        <ul>
                          {details.examples.map((example) => (
                            <li key={example}>{example}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </article>
                )
              })}
            </div>
          </>
        )}

        {sourceType === 'knowledge_base' && (
          <div className="knowledge-base-actions">
            <p>
              {selectedKnowledgeBaseIds.length} document(s) selected
            </p>

            <button
              type="button"
              onClick={() =>
                handleContinue(
                  selectedKnowledgeBaseIds,
                  setConfirmedKnowledgeBaseIds
                )
              }
              disabled={!selectedKnowledgeBaseIds.length}
            >
              Continue
            </button>
          </div>
        )}
      </section>
    )
  }


  function renderTemporaryDocumentList() {
    return (
      <section className="knowledge-base-section">
        <h2>Uploaded Documents</h2>

        {uploadListLoading && (
          <div className="loading-message">Loading uploaded documents...</div>
        )}

        {uploadListError && (
          <div className="error-message">{uploadListError}</div>
        )}

        {!uploadListLoading && uploadedDocuments.length === 0 && (
          <p>No uploaded documents yet.</p>
        )}

        {uploadedDocuments.length > 0 && (
          <>
            <div className="knowledge-base-actions">
              <p>
                {selectedUploadIds.length} of {uploadedDocuments.length} selected
              </p>

              <div>
                <button
                  type="button"
                  onClick={() =>
                    handleSelectAll(
                      uploadedDocuments.map((doc) => doc.document_id),
                      setSelectedUploadIds,
                      setConfirmedUploadIds
                    )
                  }
                >
                  Select All
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleDeselectAll(
                      setSelectedUploadIds,
                      setConfirmedUploadIds
                    )
                  }
                >
                  Deselect All
                </button>
              </div>
            </div>

            <div className="knowledge-base-list">
              {uploadedDocuments.map((document) => (
                <article
                  className="knowledge-base-card"
                  key={document.document_id}
                >
                  <div className="knowledge-base-card-header">
                    <label>
                      <input
                        type="checkbox"
                        checked={selectedUploadIds.includes(document.document_id)}
                        onChange={() =>
                          toggleId(
                            document.document_id,
                            selectedUploadIds,
                            setSelectedUploadIds,
                            setConfirmedUploadIds
                          )
                        }
                      />
                      <span>{document.filename}</span>
                    </label>

                    <span className="document-filename">
                      {document.chunks_count} chunks
                    </span>
                  </div>
                </article>
              ))}
            </div>

            {sourceType === 'upload' && (
              <div className="knowledge-base-actions">
                <p>{selectedUploadIds.length} document(s) selected</p>

                <button
                  type="button"
                  onClick={() =>
                    handleContinue(selectedUploadIds, setConfirmedUploadIds)
                  }
                  disabled={!selectedUploadIds.length}
                >
                  Continue
                </button>
              </div>
            )}
          </>
        )}
      </section>
    )
  }


  function renderWebsiteList() {
    return (
      <section className="knowledge-base-section">
        <h2>Websites</h2>

        {websiteLoading && (
          <div className="loading-message">Loading indexed websites...</div>
        )}

        {websiteListError && (
          <div className="error-message">{websiteListError}</div>
        )}

        {!websiteLoading && websites.length === 0 && (
          <p>No indexed websites yet.</p>
        )}

        {websites.length > 0 && (
          <>
            <div className="knowledge-base-actions">
              <p>
                {selectedWebsiteIds.length} of {websites.length} selected
              </p>

              <div>
                <button
                  type="button"
                  onClick={() =>
                    handleSelectAll(
                      websites.map((website) => website.document_id),
                      setSelectedWebsiteIds,
                      setConfirmedWebsiteIds
                    )
                  }
                >
                  Select All
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleDeselectAll(
                      setSelectedWebsiteIds,
                      setConfirmedWebsiteIds
                    )
                  }
                >
                  Deselect All
                </button>
              </div>
            </div>

            <div className="knowledge-base-list">
              {websites.map((website) => (
                <article
                  className="knowledge-base-card"
                  key={website.document_id}
                >
                  <div className="knowledge-base-card-header">
                    <label>
                      <input
                        type="checkbox"
                        checked={selectedWebsiteIds.includes(website.document_id)}
                        onChange={() =>
                          toggleId(
                            website.document_id,
                            selectedWebsiteIds,
                            setSelectedWebsiteIds,
                            setConfirmedWebsiteIds
                          )
                        }
                      />
                      <span>{website.page_title || website.source}</span>
                    </label>

                    <span className="document-filename">
                      {website.chunks_count} chunks
                    </span>
                  </div>

                  <p>
                    <a
                      href={website.source}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {website.source}
                    </a>
                  </p>
                </article>
              ))}
            </div>

            {sourceType === 'website' && (
              <div className="knowledge-base-actions">
                <p>{selectedWebsiteIds.length} website(s) selected</p>

                <button
                  type="button"
                  onClick={() =>
                    handleContinue(selectedWebsiteIds, setConfirmedWebsiteIds)
                  }
                  disabled={!selectedWebsiteIds.length}
                >
                  Continue
                </button>
              </div>
            )}
          </>
        )}
      </section>
    )
  }


  return (
    <main>
      <header className="app-header">
        <h1>Multi-Source RAG Assistant</h1>
        <p>Ask questions across your knowledge sources.</p>
      </header>


      <section className="source-controls">
        <h2>Choose Your Knowledge Source</h2>

        <label htmlFor="sourceType">Search in</label>

        <select
          id="sourceType"
          value={sourceType}
          onChange={handleSourceChange}
          disabled={loading || refreshing}
        >
          <option value="">Select a knowledge source</option>
          <option value="all">All Sources</option>
          <option value="knowledge_base">Knowledge Base</option>
          <option value="upload">Upload Documents</option>
          <option value="website">Websites</option>
        </select>
      </section>


      {(sourceType === 'all' || sourceType === 'knowledge_base') &&
        renderKnowledgeBaseList()}


      {(sourceType === 'all' || sourceType === 'upload') && (
        <section className="ingestion-section">
          <h2>Upload Documents</h2>

          <div className="ingestion-card">
            <p>
              Upload multiple PDF, DOCX or TXT documents. Uploaded documents are temporary.
            </p>

            <form onSubmit={handleUpload} className="upload-form">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                multiple
                onChange={(event) => {
                  setSelectedFiles(Array.from(event.target.files || []))
                  setIngestionMessage('')
                  setIngestionError('')
                }}
                disabled={uploading || refreshing}
              />

              <p>{selectedFiles.length} file(s) selected</p>

              <button
                type="submit"
                disabled={!selectedFiles.length || uploading || refreshing}
              >
                {uploading ? 'Uploading and Indexing...' : 'Upload Documents'}
              </button>
            </form>
          </div>
        </section>
      )}


      {(sourceType === 'all' || sourceType === 'upload') &&
        renderTemporaryDocumentList()}


      {(sourceType === 'all' || sourceType === 'website') && (
        <section className="ingestion-section">
          <h2>Add Websites</h2>

          <div className="ingestion-card">
            <p>
              Add a public website URL. Its content will be indexed and available for searching.
            </p>

            <form onSubmit={handleWebsiteIngestion} className="website-form">
              <input
                type="url"
                value={websiteUrl}
                onChange={(event) => setWebsiteUrl(event.target.value)}
                placeholder="https://example.com"
                required
                disabled={ingesting || refreshing}
              />

              <button
                type="submit"
                disabled={!websiteUrl.trim() || ingesting || refreshing}
              >
                {ingesting ? 'Indexing Website...' : 'Add Website'}
              </button>
            </form>
          </div>
        </section>
      )}


      {(sourceType === 'all' || sourceType === 'website') &&
        renderWebsiteList()}


      {(sourceType === 'all' || sourceType === 'upload' || sourceType === 'website') && (
        <section className="refresh-section">
          <div>
            <h2>Temporary Data Management</h2>

            <p>
              {sourceType === 'all'
                ? 'Refresh removes all uploaded documents and websites.'
                : sourceType === 'upload'
                  ? 'Refresh removes uploaded documents.'
                  : 'Refresh removes indexed websites.'}
            </p>
          </div>

          <button
            type="button"
            onClick={handleRefresh}
            disabled={refreshing || loading}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </section>
      )}


      {sourceType === '' && (
        <section className="welcome-section">
          <h2>Welcome!</h2>
          <p>
            I'm your Multi-Source RAG Assistant. Select a knowledge source above to get started.
          </p>
        </section>
      )}


      {sourceType === 'knowledge_base' && confirmedKnowledgeBaseIds.length > 0 && (
        <div className="ingestion-success">
          {confirmedKnowledgeBaseIds.length} Knowledge Base document(s) confirmed.
        </div>
      )}

      {sourceType === 'upload' && confirmedUploadIds.length > 0 && (
        <div className="ingestion-success">
          {confirmedUploadIds.length} uploaded document(s) confirmed.
        </div>
      )}

      {sourceType === 'website' && confirmedWebsiteIds.length > 0 && (
        <div className="ingestion-success">
          {confirmedWebsiteIds.length} website(s) confirmed.
        </div>
      )}


      {ingestionMessage && (
        <div className="ingestion-success" role="status">
          {ingestionMessage}
        </div>
      )}

      {ingestionError && (
        <div className="error-message" role="alert">
          {ingestionError}
        </div>
      )}


      {sourceReady && (
        <form onSubmit={handleSubmit} className="chat-form">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Enter your question..."
            rows={4}
            maxLength={2000}
            disabled={loading}
            aria-label="Enter your question"
          />

          <div className="chat-form-footer">
            {hasConversation ? (
              <button
                type="button"
                onClick={resetConversation}
                disabled={loading}
                className="clear-button"
              >
                New Chat
              </button>
            ) : (
              <button
                type="button"
                onClick={resetConversation}
                disabled={loading}
                className="clear-button"
              >
                New Chat
              </button>
            )}

            <span className="character-count">
              {question.length} / 2000 characters
            </span>
          </div>

          <button type="submit" disabled={loading || !question.trim()}>
            {loading ? 'Searching...' : 'Ask Question'}
          </button>
        </form>
      )}


      {loading && (
        <div className="loading-message" role="status">
          Searching selected sources and generating an answer...
        </div>
      )}


      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}


      {answer && (
        <section className="answer-section">
          <h2>Answer</h2>
          <div className="answer-content">
            <ReactMarkdown>{answer}</ReactMarkdown>
          </div>
        </section>
      )}


      {groupedSources.length > 0 && (
        <section className="sources-section">
          <h2>Sources ({groupedSources.length})</h2>

          {groupedSources.map((source, index) => {
            const isWebsite =
              source.source_type === 'website' &&
              typeof source.source === 'string' &&
              /^https?:\/\//i.test(source.source)

            return (
              <article
                key={`${source.source_type}::${source.source}::${index}`}
              >
                <h3>
                  {isWebsite ? (
                    <a
                      href={source.source}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {source.page_title || source.source}
                    </a>
                  ) : (
                    source.filename || source.source || 'Unknown source'
                  )}
                </h3>

                <p className="source-type">
                  Source type: {source.source_type || 'Unknown'}
                </p>

                {source.chunks.map((chunk, chunkIndex) => (
                  <p key={chunkIndex}>{chunk}</p>
                ))}
              </article>
            )
          })}
        </section>
      )}
    </main>
  )
}


export default App
