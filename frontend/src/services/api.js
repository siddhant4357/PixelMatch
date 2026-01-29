const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Admin API - Upload bulk photos
export const uploadBulkPhotos = async (files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))

  const response = await fetch(`${API_BASE_URL}/admin/upload`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Upload failed')
  }

  return response.json()
}

// Admin API - Get database statistics
export const getStats = async () => {
  const response = await fetch(`${API_BASE_URL}/admin/stats`)

  if (!response.ok) {
    throw new Error('Failed to fetch stats')
  }

  return response.json()
}

// Admin API - Reset database
export const resetDatabase = async () => {
  const response = await fetch(`${API_BASE_URL}/admin/database`, {
    method: 'DELETE'
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Reset failed')
  }

  return response.json()
}

// Guest API - Search photos by selfie
export const searchPhotosBySelfie = async (selfieFile, options = {}) => {
  const formData = new FormData()
  formData.append('selfie', selfieFile)

  if (options.similarity_threshold) {
    formData.append('similarity_threshold', options.similarity_threshold)
  }

  if (options.top_k) {
    formData.append('top_k', options.top_k)
  }

  const response = await fetch(`${API_BASE_URL}/guest/search`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Search failed')
  }

  return response.json()
}

// Guest API - Validate selfie
export const validateSelfie = async (selfieFile) => {
  const formData = new FormData()
  formData.append('selfie', selfieFile)

  const response = await fetch(`${API_BASE_URL}/guest/validate`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Validation failed')
  }

  return response.json()
}

// Get photo URL
export const getPhotoUrl = (filename) => {
  return `${API_BASE_URL}/photos/${filename}`
}

// Health check
export const healthCheck = async () => {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error('Health check failed')
  }

  return response.json()
}

// AI Search API - Upload selfie for AI search
export const uploadSelfieForAI = async (selfieFile) => {
  const formData = new FormData()
  formData.append('selfie', selfieFile)

  const response = await fetch(`${API_BASE_URL}/guest/ai-search/upload-selfie`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Selfie upload failed')
  }

  return response.json()
}

// AI Search API - Query with natural language
export const queryAI = async (sessionId, query) => {
  const response = await fetch(`${API_BASE_URL}/guest/ai-search/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      query: query
    })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'AI query failed')
  }

  return response.json()
}

// AI Search API - Get available locations
export const getAvailableLocations = async () => {
  const response = await fetch(`${API_BASE_URL}/guest/ai-search/locations`)

  if (!response.ok) {
    throw new Error('Failed to fetch locations')
  }

  return response.json()
}
