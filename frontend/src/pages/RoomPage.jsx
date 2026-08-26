import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Image as ImageIcon, Upload, Search, Settings, Loader2, ShieldCheck, CheckCircle2, Download, DownloadCloud, Sparkles } from 'lucide-react'
import { getRoomDetails, searchMyPhotos, uploadBulkPhotos, getPhotoUrl, checkConsent, grantConsent, downloadZip } from '../services/api'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'

const RoomPage = () => {
  const { roomCode } = useParams()
  const navigate = useNavigate()
  
  const [room, setRoom] = useState(null)
  const [loading, setLoading] = useState(true)
  const [hasConsent, setHasConsent] = useState(false)
  const [consenting, setConsenting] = useState(false)
  const [activeTab, setActiveTab] = useState('guest') // 'guest' or 'admin'
  const [error, setError] = useState(null)
  
  // Guest State
  const [myPhotos, setMyPhotos] = useState([])
  const [searching, setSearching] = useState(false)
  const [searchDone, setSearchDone] = useState(false)
  const [downloading, setDownloading] = useState(false)

  // Admin State
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)

  useEffect(() => {
    const fetchRoom = async () => {
      try {
        const [data, consentData] = await Promise.all([
          getRoomDetails(roomCode),
          checkConsent(roomCode)
        ])
        setRoom(data)
        setHasConsent(consentData.has_consent)
      } catch (err) {
        console.error(err)
        navigate('/dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchRoom()
  }, [roomCode, navigate])

  const handleFindPhotos = async () => {
    setSearching(true)
    setError(null)
    setSearchDone(false)
    
    try {
      // In a real app, backend would filter by room_id inside the DB
      // But for our Phase 2, vector DB might still be somewhat global or tied to the room directory
      // Assuming api.js sets localStorage so backend knows X-Room-ID
      localStorage.setItem('pixelmatch_room_id', roomCode)
      
      const res = await searchMyPhotos()
      setMyPhotos(res.matches || [])
      setSearchDone(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSearching(false)
    }
  }

  const handleDownloadAll = async () => {
    if (myPhotos.length === 0) return
    setDownloading(true)
    try {
      const filenames = myPhotos.map(photo => photo.photo_name)
      const blob = await downloadZip(roomCode, filenames)
      saveAs(blob, `${room.event_name.replace(/[^a-zA-Z0-9]/g, '_')}_Photos.zip`)
    } catch (err) {
      console.error("Error downloading zip:", err)
      alert("Failed to download photos.")
    } finally {
      setDownloading(false)
    }
  }

  const handleDownloadSingle = async (photoName, e) => {
    e.stopPropagation()
    try {
      const url = getPhotoUrl(photoName, roomCode)
      const response = await fetch(url)
      const blob = await response.blob()
      saveAs(blob, photoName)
    } catch (err) {
      console.error("Error downloading photo:", err)
    }
  }

  const handleFileSelect = (e) => {
    setFiles(Array.from(e.target.files))
    setUploadSuccess(false)
  }

  const handleUpload = async () => {
    if (files.length === 0) return
    
    setUploading(true)
    setError(null)
    try {
      localStorage.setItem('pixelmatch_room_id', roomCode)
      await uploadBulkPhotos(files)
      setUploadSuccess(true)
      setFiles([])
      // Refresh room stats
      const data = await getRoomDetails(roomCode)
      setRoom(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    )
  }

  if (!room) return null

  const handleGrantConsent = async () => {
    setConsenting(true)
    setError(null)
    try {
      await grantConsent(roomCode)
      setHasConsent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setConsenting(false)
    }
  }

  if (!hasConsent) {
    return (
      <div className="container mx-auto px-6 py-12 max-w-2xl relative z-10 flex items-center justify-center min-h-[70vh]">
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-10 sm:p-12 shadow-xl shadow-purple-900/10 border border-white text-center animate-in zoom-in-95 duration-300 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-purple-200/50 to-pink-200/50 rounded-full blur-3xl -mr-20 -mt-20"></div>
          
          <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 rounded-[2rem] flex items-center justify-center mx-auto mb-8 shadow-inner border-2 border-white relative z-10">
            <ShieldCheck className="w-12 h-12 text-purple-500" />
          </div>
          
          <h1 className="text-3xl font-extrabold text-slate-900 mb-6 tracking-tight relative z-10">
            Privacy & Consent
          </h1>
          
          <p className="text-slate-600 text-lg leading-relaxed mb-10 relative z-10">
            Your securely saved selfie will be used to automatically find photos of you in <strong>{room.event_name}</strong>. 
            For your privacy, your facial recognition data for this event will be automatically deleted after <strong>7 days</strong>.
          </p>
          
          {error && (
            <div className="mb-8 p-4 bg-red-50 text-red-700 rounded-2xl text-sm font-bold border border-red-100 relative z-10">
              {error}
            </div>
          )}
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10">
            <button 
              onClick={() => navigate('/dashboard')}
              className="w-full sm:w-auto px-8 py-4 bg-white text-slate-600 rounded-2xl font-bold hover:bg-slate-50 transition-colors border border-slate-200"
            >
              Decline
            </button>
            <button 
              onClick={handleGrantConsent}
              disabled={consenting}
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all flex items-center justify-center shadow-xl shadow-purple-500/30 disabled:opacity-50"
            >
              {consenting ? <Loader2 className="w-6 h-6 animate-spin mr-3" /> : <CheckCircle2 className="w-6 h-6 mr-3" />}
              {consenting ? 'Saving...' : 'I Agree, Find My Photos'}
            </button>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl relative z-10">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 sm:p-10 shadow-2xl shadow-purple-900/10 border border-white/80 mb-10 flex flex-col sm:flex-row items-center sm:justify-between gap-6 relative overflow-hidden ring-1 ring-purple-100/50">
        <div className="absolute -top-32 -right-32 w-96 h-96 bg-gradient-to-bl from-purple-300/40 via-pink-300/30 to-transparent rounded-full blur-3xl mix-blend-multiply animate-pulse" style={{ animationDuration: '4s' }}></div>
        <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-gradient-to-tr from-blue-300/30 via-purple-300/30 to-transparent rounded-full blur-3xl mix-blend-multiply animate-pulse" style={{ animationDuration: '6s' }}></div>
        
        <div className="relative z-10 flex flex-col sm:flex-row items-center gap-5 sm:gap-8 w-full sm:w-auto">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-400 to-pink-500 rounded-[2.5rem] blur-md opacity-40 group-hover:opacity-70 transition-opacity duration-500"></div>
            <div className="relative w-28 h-28 bg-gradient-to-br from-white to-purple-50 rounded-[2.5rem] flex items-center justify-center text-5xl shadow-inner border border-white overflow-hidden transform group-hover:scale-105 transition-transform duration-500">
               <ImageIcon className="w-12 h-12 text-purple-500" strokeWidth={1.5} />
            </div>
          </div>
          <div className="text-left flex-1">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-purple-100/50 rounded-lg text-purple-700 text-xs font-bold uppercase tracking-wider mb-3 border border-purple-200/50">
              <span className="relative flex h-2 w-2 mr-1">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
              </span>
              Live Event
            </div>
            <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">{room.event_name}</h1>
            <p className="text-slate-500 font-mono mt-3 text-lg font-medium flex items-center bg-slate-50 w-fit px-4 py-1.5 rounded-xl border border-slate-100">
               Code: <strong className="text-purple-600 ml-2 tracking-widest text-xl">{room.room_code}</strong>
            </p>
          </div>
        </div>
        
        <div className="relative z-10 bg-gradient-to-br from-white to-slate-50/80 backdrop-blur-md p-6 rounded-3xl text-center min-w-[160px] shadow-lg border border-white transform hover:-translate-y-1 transition-transform duration-300">
          <div className="absolute -top-3 -right-3">
             <div className="bg-pink-500 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow-sm animate-bounce">Total</div>
          </div>
          <div className="text-5xl font-black bg-gradient-to-br from-purple-600 to-pink-500 bg-clip-text text-transparent drop-shadow-sm">{room.photo_count || 0}</div>
          <div className="text-sm font-extrabold text-slate-400 uppercase tracking-[0.2em] mt-3">Photos</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 mb-8">
        <div className="flex gap-2 bg-white/60 backdrop-blur-md p-1.5 rounded-2xl shadow-sm border border-purple-100">
          <button 
            onClick={() => setActiveTab('guest')}
            className={`flex-1 sm:flex-none px-4 sm:px-6 py-3 rounded-xl font-bold transition-all text-sm sm:text-base ${activeTab === 'guest' ? 'bg-white text-purple-700 shadow-md' : 'text-slate-600 hover:text-purple-600'}`}
          >
            My Photos
          </button>
          <button 
            onClick={() => setActiveTab('admin')}
            className={`flex-1 sm:flex-none px-4 sm:px-6 py-3 rounded-xl font-bold flex items-center justify-center transition-all text-sm sm:text-base ${activeTab === 'admin' ? 'bg-white text-purple-700 shadow-md' : 'text-slate-600 hover:text-purple-600'}`}
          >
            <ShieldCheck className="w-4 h-4 mr-1.5" />
            Admin
          </button>
        </div>
        
        <button 
          onClick={() => navigate(`/room/${roomCode}/ask-ai`)}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-500/30"
        >
          <Sparkles className="w-4 h-4" />
          Ask AI
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-xl text-sm border border-red-100">
          {error}
        </div>
      )}

      {/* Guest Tab */}
      {activeTab === 'guest' && (
        <div className="space-y-6">
          {!searchDone && !searching && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-12 shadow-xl shadow-purple-900/5 border border-white text-center flex flex-col items-center animate-in fade-in zoom-in-95 duration-300">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center mb-8 shadow-inner">
                <Search className="w-12 h-12 text-purple-500" />
              </div>
              <h2 className="text-3xl font-extrabold text-slate-900 mb-4 tracking-tight">Find your moments</h2>
              <p className="text-slate-600 max-w-lg mx-auto mb-10 text-lg">
                We'll use your securely saved selfie to scan all {room.photo_count || 0} photos in this event and find exactly where you appear.
              </p>
              <button 
                onClick={handleFindPhotos}
                className="px-10 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all shadow-xl shadow-purple-500/30 flex items-center text-lg hover:-translate-y-1"
              >
                <Sparkles className="w-6 h-6 mr-3" />
                Find My Photos
              </button>
            </div>
          )}

          {searching && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-12 shadow-xl shadow-purple-900/5 border border-white text-center flex flex-col items-center animate-in fade-in zoom-in-95 duration-300">
              <Loader2 className="w-16 h-16 animate-spin text-purple-500 mb-6" />
              <h2 className="text-2xl font-bold text-slate-900">Scanning {room.photo_count || 0} photos...</h2>
              <p className="text-slate-600 mt-2 text-lg">Our AI is looking for your beautiful face ✨</p>
            </div>
          )}

          {searchDone && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                  {myPhotos.length === 0 ? "No photos found yet" : `Found ${myPhotos.length} photo${myPhotos.length === 1 ? '' : 's'} 🎉`}
                </h2>
                
                {myPhotos.length > 0 && (
                  <div className="flex items-center space-x-3 w-full sm:w-auto">
                    <button 
                      onClick={handleDownloadAll}
                      disabled={downloading}
                      className="flex-1 sm:flex-none text-sm font-bold text-white bg-gradient-to-r from-purple-600 to-pink-500 hover:opacity-90 transition-all shadow-md shadow-purple-500/20 px-5 py-3 rounded-xl flex items-center justify-center disabled:opacity-50"
                    >
                      {downloading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <DownloadCloud className="w-4 h-4 mr-2" />}
                      {downloading ? 'Zipping...' : 'Download All'}
                    </button>
                    <button onClick={handleFindPhotos} className="flex-1 sm:flex-none text-sm font-bold text-purple-600 hover:text-pink-500 transition-colors bg-white/80 border border-purple-100 shadow-sm px-5 py-3 rounded-xl">
                      Search Again
                    </button>
                  </div>
                )}
                {myPhotos.length === 0 && (
                  <button onClick={handleFindPhotos} className="text-sm font-bold text-purple-600 hover:text-pink-500 transition-colors bg-white/80 border border-purple-100 shadow-sm px-5 py-3 rounded-xl">
                    Search Again
                  </button>
                )}
              </div>

              {myPhotos.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                  {myPhotos.map((photo, i) => (
                    <div key={i} className="group relative aspect-square bg-slate-100 rounded-3xl overflow-hidden shadow-md border-4 border-white hover:shadow-xl transition-all duration-300">
                      <img 
                        src={getPhotoUrl(photo.photo_name, roomCode)} 
                        alt="Match" 
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-purple-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
                        <div className="flex justify-between items-center w-full">
                          <p className="text-white text-sm font-bold">{(photo.similarity * 100).toFixed(1)}% match</p>
                          <button 
                            onClick={(e) => handleDownloadSingle(photo.photo_name, e)}
                            className="bg-white/20 hover:bg-white/40 backdrop-blur-md p-2 rounded-full text-white transition-colors"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-white/60 backdrop-blur-xl rounded-[2.5rem] p-12 text-center border-2 border-purple-200 border-dashed shadow-sm">
                  <p className="text-slate-600 text-lg font-medium">Check back later when more photos are uploaded by the admin!</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Admin Tab */}
      {activeTab === 'admin' && (
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-10 shadow-xl shadow-purple-900/5 border border-white">
          <h2 className="text-2xl font-bold text-slate-900 mb-8 tracking-tight">Upload Event Photos</h2>
          
          <div className="border-4 border-dashed border-purple-200 rounded-[2rem] p-12 text-center bg-white/50 hover:bg-purple-50 hover:border-purple-400 transition-all duration-300 relative group cursor-pointer">
            <Upload className="w-16 h-16 text-purple-400 mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:text-purple-600" />
            <p className="text-slate-800 font-bold text-xl mb-2">Click to browse files</p>
            <p className="text-slate-500 font-medium">Upload JPG, PNG up to 10MB each</p>
            <input 
              type="file" 
              multiple 
              accept="image/*"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            
            {files.length > 0 && (
              <div className="mt-8 pt-8 border-t border-purple-100 text-left">
                <p className="text-sm font-bold text-purple-700 mb-4 uppercase tracking-wider">{files.length} files selected</p>
                <button 
                  onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                  disabled={uploading}
                  className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all flex items-center justify-center disabled:opacity-50 relative z-20 shadow-xl shadow-purple-500/30"
                >
                  {uploading ? <Loader2 className="w-6 h-6 animate-spin mr-3" /> : <Upload className="w-6 h-6 mr-3" />}
                  {uploading ? 'Processing & Analyzing...' : 'Upload Photos Now'}
                </button>
              </div>
            )}
            
            {uploadSuccess && (
              <div className="mt-6 p-4 bg-green-50 text-green-700 rounded-2xl text-sm font-bold flex items-center justify-center border border-green-100 shadow-sm relative z-20">
                <CheckCircle2 className="w-5 h-5 mr-2 text-green-500" /> Photos uploaded and analyzed successfully!
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default RoomPage
