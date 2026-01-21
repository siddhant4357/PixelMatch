import React from 'react'
import { Link } from 'react-router-dom'
import { Upload, Search, Zap, Shield, Users, Database, Camera } from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: <Zap className="w-12 h-12 text-yellow-400" />,
      title: 'Lightning Fast',
      description: 'MediaPipe face detection with sub-second search times'
    },
    {
      icon: <Database className="w-12 h-12 text-blue-400" />,
      title: 'Vector Database',
      description: 'ChromaDB for efficient similarity search across thousands of faces'
    },
    {
      icon: <Users className="w-12 h-12 text-green-400" />,
      title: 'Multi-Face Detection',
      description: 'Detect and index multiple faces in group photos automatically'
    },
    {
      icon: <Shield className="w-12 h-12 text-purple-400" />,
      title: 'Privacy Mode',
      description: 'Users only see photos they appear in - complete privacy'
    }
  ]

  const steps = [
    { emoji: '📤', title: 'Upload Photos', description: 'Admin uploads bulk photos to the system' },
    { emoji: '🤖', title: 'AI Processing', description: 'FaceNet detects and indexes all faces' },
    { emoji: '🤳', title: 'Upload Selfie', description: 'Guest uploads their selfie' },
    { emoji: '✨', title: 'Get Results', description: 'Instantly find all matching photos' }
  ]

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16 relative z-10">
        <div className="inline-block p-4 rounded-full bg-slate-800/50 backdrop-blur-lg border border-slate-700 mb-6 animate-fade-in-up">
          <Camera className="w-12 h-12 text-indigo-500 mx-auto" />
        </div>
        <h1 className="text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 animate-gradient">
          Welcome to PixelMatch
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
          The intelligent way to find your photos. Upload a selfie and let our AI discover your memories instantly.
        </p>

        {/* CTA Cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <Link
            to="/admin"
            className="group bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-indigo-500 transition-all hover:scale-105"
          >
            <Upload className="w-16 h-16 text-indigo-400 mx-auto mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-2xl font-bold text-white mb-3">👨‍💼 Admin Panel</h2>
            <p className="text-slate-300 mb-6">
              Upload bulk photos and let AI extract and index all faces automatically
            </p>
            <span className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold group-hover:bg-indigo-500 transition-colors">
              Go to Admin Panel →
            </span>
          </Link>

          <Link
            to="/guest"
            className="group bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-purple-500 transition-all hover:scale-105"
          >
            <Search className="w-16 h-16 text-purple-400 mx-auto mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-2xl font-bold text-white mb-3">👤 Guest Portal</h2>
            <p className="text-slate-300 mb-6">
              Upload your selfie and find all photos you appear in instantly
            </p>
            <span className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold group-hover:bg-purple-500 transition-colors">
              Find My Photos →
            </span>
          </Link>
        </div>
      </div>

      {/* How It Works */}
      <div className="mb-16">
        <h2 className="text-4xl font-bold text-center text-white mb-12">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              <div className="text-6xl mb-4">{step.emoji}</div>
              <h3 className="text-xl font-bold text-white mb-2">{index + 1}. {step.title}</h3>
              <p className="text-slate-400">{step.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="mb-16">
        <h2 className="text-4xl font-bold text-center text-white mb-12">Features</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-xl p-6 hover:border-indigo-500 transition-all"
            >
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-center text-white mb-8">Powered By</h2>
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-4xl mb-2">🧠</div>
            <h3 className="text-lg font-bold text-white mb-1">FaceNet</h3>
            <p className="text-slate-400 text-sm">Triplet Loss Architecture</p>
          </div>
          <div>
            <div className="text-4xl mb-2">⚡</div>
            <h3 className="text-lg font-bold text-white mb-1">MediaPipe</h3>
            <p className="text-slate-400 text-sm">Real-time Face Detection</p>
          </div>
          <div>
            <div className="text-4xl mb-2">🗄️</div>
            <h3 className="text-lg font-bold text-white mb-1">ChromaDB</h3>
            <p className="text-slate-400 text-sm">Vector Similarity Search</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home