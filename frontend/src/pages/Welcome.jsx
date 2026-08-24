import React from 'react'
import { Link } from 'react-router-dom'
import { Camera, Zap, Upload, ArrowRight } from 'lucide-react'
import { SignedIn, SignedOut } from '@clerk/clerk-react'

const Welcome = () => {
  return (
    <div className="min-h-screen bg-slate-50 overflow-hidden">
      {/* Hero Section */}
      <div className="relative pt-20 pb-32 sm:pt-32 sm:pb-40">
        <div className="container mx-auto px-6 relative z-10 text-center">
          <div className="inline-flex items-center space-x-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-full mb-8 border border-indigo-100">
            <span className="flex h-2 w-2 rounded-full bg-indigo-600"></span>
            <span className="text-sm font-semibold tracking-wide uppercase">PixelMatch 2.0 is Live</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 tracking-tight mb-8 leading-tight">
            Find your moments. <br />
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
              Instantly.
            </span>
          </h1>
          
          <p className="mt-6 text-xl text-slate-600 max-w-2xl mx-auto mb-12">
            No more begging for photos after an event. Join a room, snap a selfie, and let our AI instantly find every single photo of you.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <SignedOut>
              <Link
                to="/sign-up"
                className="w-full sm:w-auto px-8 py-4 bg-indigo-600 text-white rounded-xl font-bold text-lg hover:bg-indigo-700 transition-all shadow-lg hover:shadow-indigo-500/30 flex items-center justify-center"
              >
                Get Started Free <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            </SignedOut>
            <SignedIn>
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-8 py-4 bg-indigo-600 text-white rounded-xl font-bold text-lg hover:bg-indigo-700 transition-all shadow-lg hover:shadow-indigo-500/30 flex items-center justify-center"
              >
                Go to Dashboard <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            </SignedIn>
          </div>
        </div>

        {/* Decorative background blobs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-tr from-indigo-200/40 to-purple-200/40 rounded-full blur-3xl -z-10"></div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-24 sm:py-32">
        <div className="container mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">How it works</h2>
            <p className="text-slate-500">The easiest way to share and find photos from weddings, parties, and corporate events.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <FeatureCard 
              icon={<Upload className="w-8 h-8 text-indigo-500" />}
              title="1. Host Uploads"
              description="The event host creates a room and bulk uploads all the high-quality photos from the photographer."
            />
            <FeatureCard 
              icon={<Camera className="w-8 h-8 text-purple-500" />}
              title="2. Quick Selfie"
              description="Guests join the room with a code and take a quick selfie to register their face (you only do this once!)."
            />
            <FeatureCard 
              icon={<Zap className="w-8 h-8 text-pink-500" />}
              title="3. Instant Magic"
              description="Our advanced AI scans the album and instantly delivers a personalized gallery of just your photos."
            />
          </div>
        </div>
      </div>
    </div>
  )
}

const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-slate-50 p-8 rounded-3xl border border-slate-100 text-center hover:shadow-lg transition-shadow">
    <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mx-auto mb-6">
      {icon}
    </div>
    <h3 className="text-xl font-bold text-slate-900 mb-3">{title}</h3>
    <p className="text-slate-600 leading-relaxed">{description}</p>
  </div>
)

export default Welcome
