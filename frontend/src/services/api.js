const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// --- Room Context Management ---

export const setRoomId = (roomId) => {
  if (roomId) {
    localStorage.setItem('pixelmatch_room_id', roomId)
  } else {
    localStorage.removeItem('pixelmatch_room_id')
  }
}

export const getRoomId = () => {
  return localStorage.getItem('pixelmatch_room_id')
}

export const getRoomInfo = () => {
  const info = localStorage.getItem('pixelmatch_room_info')
  return info ? JSON.parse(info) : null
}

export const setRoomInfo = (info) => {
  if (info) {
    localStorage.setItem('pixelmatch_room_info', JSON.stringify(info))
    setRoomId(info.room_id)
  } else {
    localStorage.removeItem('pixelmatch_room_info')
    setRoomId(null)
  }
}

// --- Request Wrapper ---

const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`

  const headers = options.headers || {}

  // Inject Room ID if it exists
  const roomId = getRoomId()
  if (roomId) {
    headers['X-Room-ID'] = roomId
  }

  const config = {
    ...options,
    headers: headers
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    // Try to parse error message
    let errorMessage = 'Request failed'
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch (e) {
      // If parsing fails, use status text
      errorMessage = response.statusText || errorMessage
    }
    throw new Error(errorMessage)
  }

  return response.json()
}

// --- API Functions ---

// Room API
export const createRoom = async (eventName, password) => {
  return request('/api/rooms/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event_name: eventName, password: password })
  })
}

export const joinRoom = async (roomId) => {
  return request('/api/rooms/join', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room_id: roomId })
  })
}

// Admin API - Upload bulk photos
export const uploadBulkPhotos = async (files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))

  // Note: Content-Type header excluded for FormData to let browser set boundary
  return request('/admin/upload', {
    method: 'POST',
    body: formData
  })
}

// Admin API - Get database statistics
export const getStats = async () => {
  return request('/admin/stats')
}

// Admin API - Reset database
export const resetDatabase = async (password) => {
  return request('/admin/database/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: password })
  })
}

// Admin API - Import from Google Drive
export const importFromDrive = async (url) => {
  return request('/admin/import-drive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url })
  })
}

// Admin API - Get task status
export const getTaskStatus = async (taskId) => {
  return request(`/admin/task-status/${taskId}`)
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

  return request('/guest/search', {
    method: 'POST',
    body: formData
  })
}

// Guest API - Validate selfie
export const validateSelfie = async (selfieFile) => {
  const formData = new FormData()
  formData.append('selfie', selfieFile)

  return request('/guest/validate', {
    method: 'POST',
    body: formData
  })
}

// Get photo URL (Helper, not async)
export const getPhotoUrl = (filename) => {
  let url = `${API_BASE_URL}/photos/${filename}`
  // We can't easily add headers to img src, so we might need a proxy or signed URL if strict auth was needed.
  // But for now, we depend on the backend checking X-Room-ID?
  // Wait, if we use <img src="..."> we CANNOT send custom headers.
  // Ideally, the room context should be part of the URL path if we want standard img tags to work.
  // OR, we depend on the filename being unique enough (uuids) or we accept that room isolation is logical, not physical security.
  // But wait, my backend requires X-Room-ID for /photos/{filename} now!
  // This breaks <img src>!

  // Quick fix: Backend should allow query param as fallback for X-Room-ID?
  // Or simpler: Include room_id in the URL construction if available.
  // The backend endpoint is /photos/{filename}. 
  // I should update backend to accept `?room_id=...` as well if headers are missing.

  const roomId = getRoomId()
  // But backend currently only looks at Header.
  // I'll need to update backend to fallback to query param for file serving.

  if (roomId) {
    url += `?room_id=${roomId}`
  }

  return url
}

// Health check
export const healthCheck = async () => {
  return request('/health')
}

// AI Search API - Upload selfie for AI search
export const uploadSelfieForAI = async (selfieFile) => {
  const formData = new FormData()
  formData.append('selfie', selfieFile)

  return request('/guest/ai-search/upload-selfie', {
    method: 'POST',
    body: formData
  })
}

// AI Search API - Query with natural language
export const queryAI = async (sessionId, query) => {
  return request('/guest/ai-search/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      query: query
    })
  })
}

// AI Search API - Get available locations
export const getAvailableLocations = async () => {
  return request('/guest/ai-search/locations')
}

// AI Search API - Get Metadata Stats
export const getMetadataStats = async () => {
  return request('/admin/stats/metadata')
}
