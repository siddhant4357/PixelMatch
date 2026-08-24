import React, { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Camera, Upload, Loader2, CheckCircle2, Sparkles, ArrowLeft } from 'lucide-react'
import Webcam from 'react-webcam'
import { uploadSelfie } from '../services/api'

const Onboarding = () => {
  const navigate = useNavigate()
  const [method, setMethod] = useState(null)
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const webcamRef = useRef(null)

  const handleCapture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot()
    setPreview(imageSrc)
    
    fetch(imageSrc)
      .then(res => res.blob())
      .then(blob => {
        const capturedFile = new File([blob], "webcam_selfie.jpg", { type: "image/jpeg" })
        setFile(capturedFile)
      })
  }, [webcamRef])

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setMethod('upload')
    }
  }

  const handleSubmit = async () => {
    if (!file) return
    
    setLoading(true)
    setError(null)
    try {
      await uploadSelfie(file)
      setSuccess(true)
      setTimeout(() => navigate('/dashboard'), 2000)
    } catch (err) {
      setError(err.message || "Failed to save selfie. Please make sure your face is clearly visible.")
      setLoading(false)
    }
  }

  const resetSelection = () => {
    setMethod(null)
    setFile(null)
    setPreview(null)
    setError(null)
  }

  if (success) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center animate-in fade-in duration-500">
        <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-6 shadow-lg shadow-green-200/50">
          <CheckCircle2 className="w-12 h-12 text-green-500" />
        </div>
        <h2 className="text-4xl font-extrabold text-slate-800 mb-2">You're all set!</h2>
        <p className="text-xl text-slate-600">Taking you to your dashboard...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0] pt-12 pb-24 px-6 relative">
      {/* Decorative */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-gradient-to-br from-purple-300/30 to-pink-300/30 blur-3xl" />
      
      <div className="max-w-3xl mx-auto relative z-10">
        <div className="text-center mb-10">
          <div className="inline-flex p-4 rounded-2xl bg-white/60 backdrop-blur-md shadow-lg shadow-purple-200/50 mb-6">
            <Camera className="w-10 h-10 text-purple-600" />
          </div>
          <h1 className="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">One Last Step! <Sparkles className="inline w-8 h-8 text-pink-500" /></h1>
          <p className="text-lg text-slate-700 max-w-xl mx-auto">
            Take or upload a clear photo of your face. We'll use this to instantly find your photos across all events you join!
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-xl shadow-purple-900/5 border border-white p-8 sm:p-12">
          {error && (
            <div className="mb-8 p-4 bg-red-50 text-red-700 rounded-2xl text-sm font-medium border border-red-100 flex items-center">
              <div className="w-2 h-2 rounded-full bg-red-500 mr-3"></div>
              {error}
            </div>
          )}

          {!method && !preview && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <button 
                onClick={() => setMethod('camera')}
                className="group flex flex-col items-center justify-center p-12 border-2 border-dashed border-purple-200 rounded-[2rem] hover:bg-gradient-to-br hover:from-purple-50 hover:to-pink-50 hover:border-purple-400 transition-all duration-300"
              >
                <div className="w-20 h-20 bg-white shadow-md rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Camera className="w-10 h-10 text-purple-600" />
                </div>
                <span className="font-bold text-xl text-slate-800">Take a Photo</span>
                <span className="text-sm text-slate-500 mt-2">Use your camera</span>
              </button>

              <div className="relative group">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  title="Upload from device"
                />
                <div className="h-full flex flex-col items-center justify-center p-12 border-2 border-dashed border-pink-200 rounded-[2rem] group-hover:bg-gradient-to-br group-hover:from-pink-50 group-hover:to-orange-50 group-hover:border-pink-400 transition-all duration-300">
                  <div className="w-20 h-20 bg-white shadow-md rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <Upload className="w-10 h-10 text-pink-500" />
                  </div>
                  <span className="font-bold text-xl text-slate-800">Upload File</span>
                  <span className="text-sm text-slate-500 mt-2">Browse your gallery</span>
                </div>
              </div>
            </div>
          )}

          {method === 'camera' && !preview && (
            <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
              <div className="w-full max-w-md rounded-[2rem] overflow-hidden bg-slate-900 shadow-2xl mb-8 border-4 border-white">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{ facingMode: "user" }}
                  className="w-full"
                />
              </div>
              <div className="flex space-x-4 w-full max-w-md">
                <button 
                  onClick={resetSelection}
                  className="py-4 px-6 bg-white text-slate-700 rounded-2xl font-bold hover:bg-slate-50 transition-colors shadow-sm border border-slate-200"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <button 
                  onClick={handleCapture}
                  className="flex-1 py-4 px-8 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-opacity flex items-center justify-center shadow-xl shadow-purple-500/30"
                >
                  <Camera className="w-6 h-6 mr-2" />
                  Capture Photo
                </button>
              </div>
            </div>
          )}

          {preview && (
            <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
              <div className="relative w-64 h-64 mb-10">
                <img 
                  src={preview} 
                  alt="Selfie Preview" 
                  className="w-full h-full object-cover rounded-full shadow-2xl border-8 border-white"
                />
                <div className="absolute inset-0 rounded-full ring-[6px] ring-purple-500/30 ring-offset-4"></div>
              </div>
              
              <div className="flex space-x-4 w-full max-w-md">
                <button 
                  onClick={resetSelection}
                  disabled={loading}
                  className="py-4 px-6 bg-white text-slate-700 rounded-2xl font-bold hover:bg-slate-50 transition-colors shadow-sm border border-slate-200 disabled:opacity-50"
                >
                  Retake
                </button>
                <button 
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex-1 py-4 px-8 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all flex items-center justify-center shadow-xl shadow-purple-500/30 disabled:opacity-50"
                >
                  {loading ? (
                    <><Loader2 className="w-6 h-6 mr-2 animate-spin" /> Saving...</>
                  ) : (
                    'Looks Perfect! 🚀'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Onboarding
