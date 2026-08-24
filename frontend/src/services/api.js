const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// --- Auth Token Management ---
let getTokenFn = null

export const setTokenProvider = (fn) => {
  getTokenFn = fn
}

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

// --- Request Wrapper ---
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = options.headers || {}

  // Inject Auth Token
  if (getTokenFn) {
    const token = await getTokenFn()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  // Inject Room ID for backward compatibility
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
    let errorMessage = 'Request failed'
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch (e) {
      errorMessage = response.statusText || errorMessage
    }
    throw new Error(errorMessage)
  }

  return response.json()
}

// --- Auth API ---
export const getProfile = async () => {
  return request('/auth/profile')
}

export const uploadSelfie = async (file) => {
  const formData = new FormData()
  formData.append('selfie', file)
  return request('/auth/upload-selfie', {
    method: 'POST',
    body: formData
  })
}

export const updateSelfie = async (file) => {
  const formData = new FormData()
  formData.append('selfie', file)
  return request('/auth/update-selfie', {
    method: 'PUT',
    body: formData
  })
}

export const deleteMyData = async () => {
  return request('/auth/delete-data', {
    method: 'DELETE'
  })
}


// --- Room API ---
export const createRoom = async (eventName, password) => {
  return request('/api/rooms/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event_name: eventName, password: password })
  })
}

export const joinRoom = async (roomCode) => {
  return request('/api/rooms/join', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room_code: roomCode })
  })
}

export const getMyRooms = async () => {
  return request('/api/rooms/my-rooms')
}

export const getRoomDetails = async (roomCode) => {
  return request(`/api/rooms/${roomCode}`)
}

export const checkConsent = async (roomCode) => {
  return request(`/api/rooms/${roomCode}/consent`)
}

export const grantConsent = async (roomCode) => {
  return request(`/api/rooms/${roomCode}/consent`, {
    method: 'POST'
  })
}


// --- Guest API ---
export const searchMyPhotos = async (options = {}) => {
  const params = new URLSearchParams()
  if (options.similarity_threshold) params.append('similarity_threshold', options.similarity_threshold)
  if (options.top_k) params.append('top_k', options.top_k)
  
  return request(`/guest/search?${params.toString()}`, {
    method: 'POST'
  })
}

export const queryAI = async (query) => {
  return request('/ai/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  })
}

// One-off search with file (if ever needed)
export const searchPhotosBySelfie = async (selfieFile, options = {}) => {
  const formData = new FormData()
  formData.append('selfie', selfieFile)
  if (options.similarity_threshold) formData.append('similarity_threshold', options.similarity_threshold)
  if (options.top_k) formData.append('top_k', options.top_k)

  return request('/guest/search-with-selfie', {
    method: 'POST',
    body: formData
  })
}


// --- Admin API ---
export const uploadBulkPhotos = async (files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  return request('/admin/upload', {
    method: 'POST',
    body: formData
  })
}

export const getStats = async () => {
  return request('/admin/stats')
}

export const resetDatabase = async (password) => {
  // Adding empty body if none needed, backend gets password from header or it expects it from header?
  // Our new backend endpoint doesn't accept password in body, it accepts X-Room-ID and maybe we should pass password somewhere.
  // Actually, wait, backend expects header X-Room-ID.
  return request('/admin/database/reset', {
    method: 'POST'
  })
}

// --- Helpers ---
export const getPhotoUrl = (filename, roomCode = null) => {
  const rCode = roomCode || localStorage.getItem('pixelmatch_room_id')
  if (!rCode) return `${API_BASE_URL}/guest/photos/${filename}`
  return `${API_BASE_URL}/guest/photos/${rCode}/${filename}`
}

export const downloadZip = async (roomCode, filenames) => {
  const response = await fetch(`${API_BASE_URL}/guest/photos/${roomCode}/download-zip`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ filenames })
  })
  if (!response.ok) throw new Error("Failed to download zip")
  return response.blob()
}

export const healthCheck = async () => {
  return request('/health')
}
