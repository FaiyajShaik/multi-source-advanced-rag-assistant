
const API_BASE_URL = 'http://127.0.0.1:8000'

async function handleResponse(response, fallbackMessage) {
  let data

  try {
    data = await response.json()
  } catch {
    throw new Error(fallbackMessage)
  }

  if (!response.ok) {
    const detail = data.detail

    if (typeof detail === 'string') {
      throw new Error(detail)
    }

    if (detail && typeof detail === 'object') {
      const failures = detail.failures || []

      const failureMessages = failures
        .map((failure) => {
          if (failure.filename && failure.error) {
            return `${failure.filename}: ${failure.error}`
          }

          return failure.error || ''
        })
        .filter(Boolean)

      if (failureMessages.length > 0) {
        throw new Error(failureMessages.join('\n'))
      }

      throw new Error(detail.message || fallbackMessage)
    }

    throw new Error(fallbackMessage)
  }

  return data
}

export async function askQuestion(
  question,
  sourceType = 'all',
  documentIds = null
) {
  const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      source_type: sourceType,
      document_ids: documentIds,
    }),
  })

  return handleResponse(response, 'Failed to get an answer.')
}

export async function getKnowledgeBaseDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/knowledge-base`
  )

  return handleResponse(
    response,
    'Failed to load Knowledge Base documents.'
  )
}

export async function getUploadedDocuments() {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/uploads`
  )

  return handleResponse(
    response,
    'Failed to load uploaded documents.'
  )
}

export async function getIndexedWebsites() {
  const response = await fetch(`${API_BASE_URL}/api/v1/websites`)

  return handleResponse(
    response,
    'Failed to load indexed websites.'
  )
}

export async function uploadDocuments(files) {
  const formData = new FormData()

  for (const file of files) {
    formData.append('files', file)
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/upload`,
    {
      method: 'POST',
      body: formData,
    }
  )

  return handleResponse(response, 'Document upload failed.')
}

export async function ingestWebsite(url) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/websites/ingest`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    }
  )

  return handleResponse(response, 'Website ingestion failed.')
}

export async function refreshTemporaryData() {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/refresh`,
    { method: 'POST' }
  )

  return handleResponse(
    response,
    'Failed to refresh temporary data.'
  )
}
