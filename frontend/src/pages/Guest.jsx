import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Upload, AlertCircle, Sliders, Download, Sparkles } from 'lucide-react'
import { searchPhotosBySelfie, getPhotoUrl } from '../services/api'

const Guest = () => {
  const [selfieFile, setSelfieFile] = useState(null)
  const [selfiePreview, setSelfiePreview] = useState(null)
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [threshold, setThreshold] = useState(0.50)  // Match backend default
  const [maxResults, setMaxResults] = useState(50)

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelfieFile(file)

      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => setSelfiePreview(e.target.result)
      reader.readAsDataURL(file)
    }
  }

  const handleSearch = async () => {
    if (!selfieFile) return

    setSearching(true)
    setError(null)
    setResults(null)

    try {
      const data = await searchPhotosBySelfie(selfieFile, {
        similarity_threshold: threshold,
        top_k: maxResults
      })
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-white mb-4">Find My Photos</h1>
        <p className="text-xl text-slate-300 mb-6">Upload your selfie to find all photos you appear in</p>

        {/* Ask AI Button */}
        <Link
          to="/guest/ask-ai"
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-500 hover:to-pink-500 transition-all shadow-lg hover:shadow-xl"
        >
          <Sparkles className="w-5 h-5" />
          <span>Try Ask AI - Search with Natural Language!</span>
        </Link>
      </div>

      {/* Upload Section */}
      <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 mb-8">
        <h2 className="text-2xl font-bold text-white mb-6">Upload Your Selfie</h2>

        {/* File Input */}
        <div className="mb-6">
          <input
            type="file"
            id="selfieInput"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          <label
            htmlFor="selfieInput"
            className="block border-2 border-dashed border-slate-600 hover:border-slate-500 rounded-xl p-12 text-center cursor-pointer transition-all"
          >
            <Upload className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <div className="text-xl font-semibold text-white mb-2">
              Click to select your selfie
            </div>
            <div className="text-slate-400">
              Make sure your face is clearly visible
            </div>
          </label>
        </div>

        {/* Preview */}
        {selfiePreview && (
          <div className="mb-6 text-center">
            <img
              src={selfiePreview}
              alt="Selfie preview"
              className="max-w-xs mx-auto rounded-xl border-2 border-slate-600"
            />
            <div className="text-slate-400 mt-2">{selfieFile?.name}</div>
          </div>
        )}

        {/* Settings */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="flex items-center space-x-2 text-white font-semibold mb-2">
              <Sliders className="w-4 h-4" />
              <span>Similarity Threshold</span>
            </label>
            <input
              type="range"
              min="0.3"
              max="0.9"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-center text-slate-400 text-sm mt-1">
              {threshold.toFixed(2)} - Auto finds difficult photos
            </div>
            <div className="text-xs text-slate-500 text-center mt-1">
              💡 Default 0.50 is balanced. Lower for more results.
            </div>
          </div>

          <div>
            <label className="text-white font-semibold mb-2 block">Max Results</label>
            <input
              type="number"
              min="10"
              max="100"
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={!selfieFile || searching}
          className="w-full px-6 py-4 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
        >
          {searching ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Search for My Photos</span>
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-xl p-4 mb-8 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-red-500">Error</div>
            <div className="text-red-400">{error}</div>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div>
          {results.total_matches === 0 ? (
            <div className="bg-yellow-500/10 border border-yellow-500 rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">😕</div>
              <div className="font-semibold text-yellow-500 text-lg mb-2">No matches found</div>
              <div className="text-yellow-400">
                {results.message || 'Try adjusting the similarity threshold or upload a clearer selfie.'}
              </div>
            </div>
          ) : (
            <>
              <div className="bg-green-500/10 border border-green-500 rounded-xl p-4 mb-8">
                <div className="font-semibold text-green-500 text-lg">
                  ✅ Found {results.total_matches} photo(s) containing you!
                </div>
              </div>

              <h3 className="text-2xl font-bold text-white mb-6">Top Matches</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {results.matches.filter(m => m.max_similarity >= 0.50).map((match, index) => (
                  <div
                    key={index}
                    className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden hover:border-indigo-500 transition-all group"
                  >
                    <img
                      src={getPhotoUrl(match.photo_name)}
                      alt={match.photo_name}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-4">
                      <div className="text-white font-semibold text-sm mb-2 truncate">
                        {match.photo_name}
                      </div>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex flex-col gap-1">
                          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${match.max_similarity >= 0.75 ? 'bg-green-500 text-white' :
                            match.max_similarity >= 0.60 ? 'bg-blue-500 text-white' :
                              match.max_similarity >= 0.50 ? 'bg-yellow-500 text-white' :
                                'bg-orange-500 text-white'
                            }`}>
                            {Math.round(match.max_similarity * 100)}% match
                          </span>
                          <span className="text-xs text-slate-400">
                            {match.is_expanded ? '🚀 Smart Expand' :
                              match.max_similarity >= 0.75 ? '✨ Excellent' :
                                match.max_similarity >= 0.60 ? '👍 Good' :
                                  match.max_similarity >= 0.50 ? '⚠️ Fair' :
                                    '🔍 Review'}
                          </span>
                        </div>
                        <span className="text-slate-400 text-xs">
                          {match.face_count} face(s)
                        </span>
                      </div>
                      <a
                        href={getPhotoUrl(match.photo_name)}
                        download
                        className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {results.matches.filter(m => m.max_similarity < 0.50).length > 0 && (
                <>
                  <div className="border-t border-slate-700 my-8"></div>
                  <h3 className="text-xl font-bold text-slate-300 mb-6 flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2 text-orange-500" />
                    Possible Matches (Low Confidence)
                  </h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-80 hover:opacity-100 transition-opacity">
                    {results.matches.filter(m => m.max_similarity < 0.50).map((match, index) => (
                      <div
                        key={`low-${index}`}
                        className="bg-slate-800/30 border border-slate-700/50 rounded-xl overflow-hidden hover:border-orange-500/50 transition-all group"
                      >
                        <img
                          src={getPhotoUrl(match.photo_name)}
                          alt={match.photo_name}
                          className="w-full h-48 object-cover grayscale group-hover:grayscale-0 transition-all"
                        />
                        <div className="p-4">
                          <div className="text-slate-300 font-medium text-sm mb-2 truncate">
                            {match.photo_name}
                          </div>
                          <div className="flex items-center justify-between mb-3">
                            <span className="px-3 py-1 bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-full text-sm font-semibold">
                              {Math.round(match.max_similarity * 100)}% maybe
                            </span>
                            <span className="text-slate-500 text-xs">
                              Review carefully
                            </span>
                          </div>
                          <a
                            href={getPhotoUrl(match.photo_name)}
                            download
                            className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2"
                          >
                            <Download className="w-4 h-4" />
                            <span>Download</span>
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default Guest