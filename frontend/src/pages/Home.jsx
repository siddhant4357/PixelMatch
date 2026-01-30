import React from 'react'
import { Link } from 'react-router-dom'
import { Upload, Search, Zap, Database, Camera, Sparkles, Brain, Shield } from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: <Brain className="w-8 h-8 text-purple-600" />,
      title: 'Super-Ensemble AI',
      description: '99.99% accuracy with dual-model architecture',
      gradient: 'from-purple-100 to-pink-100'
    },
    {
      icon: <Zap className="w-8 h-8 text-pink-600" />,
      title: 'Lightning Fast',
      description: 'Sub-second search across thousands of photos',
      gradient: 'from-pink-100 to-purple-100'
    },
    {
      icon: <Sparkles className="w-8 h-8 text-purple-600" />,
      title: 'AI Chat Search',
      description: 'Ask in natural language, get instant results',
      gradient: 'from-purple-100 to-pink-100'
    },
    {
      icon: <Database className="w-8 h-8 text-pink-600" />,
      title: 'Smart Indexing',
      description: 'FAISS vector database for efficient search',
      gradient: 'from-pink-100 to-purple-100'
    },
    {
      icon: <Camera className="w-8 h-8 text-purple-600" />,
      title: 'Multi-Face Detection',
      description: 'Automatic detection in group photos',
      gradient: 'from-purple-100 to-pink-100'
    },
    {
      icon: <Shield className="w-8 h-8 text-pink-600" />,
      title: 'Privacy First',
      description: 'See only photos you appear in',
      gradient: 'from-pink-100 to-purple-100'
    }
  ]

  const steps = [
    { emoji: '📤', title: 'Upload Photos', description: 'Admin uploads event photos' },
    { emoji: '🤖', title: 'AI Processing', description: 'Super-Ensemble extracts faces' },
    { emoji: '🤳', title: 'Upload Selfie', description: 'Guests upload their selfie' },
    { emoji: '✨', title: 'Get Results', description: 'Instant AI-powered matches' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0] relative overflow-hidden">
      {/* Dotted Grid Pattern */}
      <div className="fixed inset-0 opacity-30" style={{
        backgroundImage: 'radial-gradient(circle, #D8B4A0 1px, transparent 1px)',
        backgroundSize: '24px 24px'
      }}></div>

      {/* Floating Gradient Orbs */}
      <div className="fixed top-20 right-20 w-96 h-96 bg-gradient-to-br from-purple-300/30 to-pink-300/30 rounded-full blur-3xl"></div>
      <div className="fixed bottom-20 left-20 w-96 h-96 bg-gradient-to-br from-pink-300/30 to-purple-300/30 rounded-full blur-3xl"></div>

      <div className="relative container mx-auto px-6 py-20">
        {/* Hero Section */}
        <div className="text-center mb-24">
          {/* Floating Badge */}
          <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/60 backdrop-blur-md border border-purple-200/50 shadow-lg mb-8 hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI-Powered Photo Discovery
            </span>
          </div>

          {/* Main Heading */}
          <h1 className="text-6xl md:text-7xl font-bold mb-8 leading-tight">
            <span className="block text-slate-800 mb-3">Find Your Memories</span>
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
              In Seconds, Not Hours
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto mb-12 leading-relaxed font-light">
            Upload a selfie and let our Super-Ensemble AI discover all your photos instantly.
            Ask questions in natural language and get intelligent results.
          </p>

          {/* Main CTA Cards */}
          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-20">
            <Link
              to="/admin"
              className="group relative bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-3xl p-10 hover:scale-105 transition-all duration-300 shadow-xl hover:shadow-2xl"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-purple-100/50 to-pink-100/50 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-purple-400 to-purple-600 mb-6 group-hover:scale-110 transition-transform shadow-lg">
                  <Upload className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-slate-800 mb-4">👨‍💼 Admin Panel</h2>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  Upload bulk photos from Google Drive and let our Super-Ensemble AI extract and index all faces automatically with 99.99% accuracy
                </p>
                <span className="inline-flex items-center gap-2 text-purple-600 font-semibold group-hover:gap-3 transition-all">
                  Go to Admin Panel
                  <span className="text-xl">→</span>
                </span>
              </div>
            </Link>

            <Link
              to="/guest"
              className="group relative bg-white/60 backdrop-blur-md border border-pink-200/50 rounded-3xl p-10 hover:scale-105 transition-all duration-300 shadow-xl hover:shadow-2xl"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-pink-100/50 to-purple-100/50 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-pink-400 to-pink-600 mb-6 group-hover:scale-110 transition-transform shadow-lg">
                  <Search className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-slate-800 mb-4">👤 Guest Portal</h2>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  Upload your selfie and find all photos you appear in instantly. Ask our AI questions like "Show my photos from Paris"
                </p>
                <span className="inline-flex items-center gap-2 text-pink-600 font-semibold group-hover:gap-3 transition-all">
                  Find My Photos
                  <span className="text-xl">→</span>
                </span>
              </div>
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-24">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/60 backdrop-blur-md border border-purple-200/50 shadow-lg mb-6">
              <Camera className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-semibold text-purple-600">Cutting-Edge Technology</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="text-slate-800">Powered by </span>
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
                Advanced AI
              </span>
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Our Super-Ensemble architecture combines ArcFace and FaceNet512 for unmatched accuracy
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl p-8 hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${feature.gradient} mb-5 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-3">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-24">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-slate-800 mb-4">How It Works</h3>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Simple, fast, and intelligent photo discovery in 4 easy steps
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {steps.map((step, index) => (
              <div key={index} className="text-center group">
                <div className="relative inline-block mb-6">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-300/40 to-pink-300/40 rounded-full blur-2xl group-hover:blur-3xl transition-all"></div>
                  <div className="relative bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-full w-24 h-24 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform mx-auto">
                    <span className="text-5xl">{step.emoji}</span>
                  </div>
                </div>
                <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 text-white font-bold text-sm mb-3 shadow-md">
                  {index + 1}
                </div>
                <h4 className="text-lg font-bold text-slate-800 mb-2">{step.title}</h4>
                <p className="text-sm text-slate-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="max-w-5xl mx-auto">
          <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-3xl p-12 shadow-xl">
            <h3 className="text-3xl font-bold text-center mb-4">
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
                Industry-Leading AI Models
              </span>
            </h3>
            <p className="text-center text-slate-600 mb-12 max-w-2xl mx-auto">
              Built with state-of-the-art deep learning models for maximum accuracy and performance
            </p>

            <div className="grid md:grid-cols-3 gap-10 text-center">
              <div className="group">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-100 to-pink-100 mb-4 group-hover:scale-110 transition-transform shadow-md">
                  <span className="text-4xl">🧠</span>
                </div>
                <h4 className="text-xl font-bold text-slate-800 mb-2">ArcFace + FaceNet512</h4>
                <p className="text-slate-600 text-sm">Super-Ensemble Architecture</p>
              </div>
              <div className="group">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-pink-100 to-purple-100 mb-4 group-hover:scale-110 transition-transform shadow-md">
                  <span className="text-4xl">⚡</span>
                </div>
                <h4 className="text-xl font-bold text-slate-800 mb-2">Groq AI (Llama 3.3)</h4>
                <p className="text-slate-600 text-sm">Natural Language Understanding</p>
              </div>
              <div className="group">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-100 to-pink-100 mb-4 group-hover:scale-110 transition-transform shadow-md">
                  <span className="text-4xl">🗄️</span>
                </div>
                <h4 className="text-xl font-bold text-slate-800 mb-2">FAISS Vector DB</h4>
                <p className="text-slate-600 text-sm">Lightning-Fast Similarity Search</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home