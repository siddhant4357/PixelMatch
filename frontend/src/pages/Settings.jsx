import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2, AlertTriangle, User, ShieldAlert, Loader2 } from 'lucide-react'
import { getProfile, deleteMyData } from '../services/api'
import { useClerk } from '@clerk/clerk-react'

const Settings = () => {
  const navigate = useNavigate()
  const { signOut } = useClerk()
  
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getProfile()
        setProfile(data.user)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchProfile()
  }, [])

  const handleDeleteData = async () => {
    if (!window.confirm("Are you absolutely sure? This will delete your facial recognition embedding from our database. You will no longer be able to find your photos in events unless you re-upload a selfie.")) return
    
    setIsDeleting(true)
    setError(null)
    try {
      await deleteMyData()
      alert("All your selfie data has been deleted from our servers.")
      // Might want to sign out or go to onboarding
      navigate('/onboarding')
    } catch (err) {
      setError(err.message)
      setIsDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-3xl relative z-10">
      <h1 className="text-4xl font-extrabold text-slate-900 mb-10 tracking-tight">Account Settings</h1>
      
      {/* Profile Info */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-xl shadow-purple-900/5 border border-white p-10 mb-10">
        <div className="flex items-center space-x-6 mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center overflow-hidden shadow-inner border-2 border-white">
            {profile?.avatar_url ? (
              <img src={profile.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
            ) : (
              <User className="w-10 h-10 text-purple-400" />
            )}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">{profile?.name || "User"}</h2>
            <p className="text-slate-500 text-lg">{profile?.email}</p>
          </div>
        </div>
        
        <button 
          onClick={() => navigate('/onboarding')}
          className="px-6 py-3 bg-purple-50 text-purple-700 rounded-2xl font-bold hover:bg-purple-100 transition-colors border border-purple-100"
        >
          Update Registered Selfie
        </button>
      </div>

      {/* Danger Zone */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-xl shadow-red-900/5 border border-red-100 p-10">
        <h2 className="text-2xl font-bold text-slate-900 mb-3 flex items-center">
          <ShieldAlert className="w-6 h-6 text-red-500 mr-3" />
          Privacy & Data
        </h2>
        <p className="text-slate-600 mb-8 text-lg">
          We respect your privacy. If you no longer want us to store your facial embedding for matching photos, you can delete it permanently here.
        </p>
        
        {error && <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-2xl text-sm font-medium border border-red-100">{error}</div>}
        
        <button 
          onClick={handleDeleteData}
          disabled={isDeleting}
          className="px-6 py-4 bg-red-50 text-red-600 rounded-2xl font-bold hover:bg-red-100 border border-red-200 transition-colors flex items-center disabled:opacity-50"
        >
          {isDeleting ? <Loader2 className="w-5 h-5 animate-spin mr-3" /> : <Trash2 className="w-5 h-5 mr-3" />}
          Delete My Face Data
        </button>
      </div>
    </div>
  )
}

export default Settings
