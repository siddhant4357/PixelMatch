import React, { useState, useEffect } from 'react'
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle, Database, Trash2 } from 'lucide-react'
import { uploadBulkPhotos, getStats, resetDatabase } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ProgressLoader from '../components/ProgressLoader'
import SuccessModal from '../components/SuccessModal'

const Admin = () => {
    const [selectedFiles, setSelectedFiles] = useState([])
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [uploadCurrent, setUploadCurrent] = useState(0)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [stats, setStats] = useState(null)
    const [dragActive, setDragActive] = useState(false)

    // Load stats on mount
    const [driveUrl, setDriveUrl] = useState('');
    const [taskId, setTaskId] = useState(null);
    const [driveStatus, setDriveStatus] = useState(null);
    const [showSuccessModal, setShowSuccessModal] = useState(false);

    useEffect(() => {
        loadStats();
    }, []);

    // Polling for Drive Status
    const alertShownRef = React.useRef(false);

    useEffect(() => {
        let interval;
        if (taskId) {
            // Reset alert flag when new task starts
            alertShownRef.current = false;

            interval = setInterval(async () => {
                try {
                    const res = await fetch(`http://localhost:8000/admin/task-status/${taskId}`);
                    const data = await res.json();
                    setDriveStatus(data);

                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(interval);
                        loadStats(); // Update stats on valid completion

                        // Only show modal once per task
                        if (data.status === 'completed' && !alertShownRef.current) {
                            alertShownRef.current = true;
                            setShowSuccessModal(true);
                        }
                    }
                } catch (e) {
                    console.error("Polling error", e);
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [taskId]);

    const handleDriveImport = async () => {
        if (!driveUrl) return;
        try {
            const res = await fetch('http://localhost:8000/admin/import-drive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: driveUrl })
            });
            const data = await res.json();
            setTaskId(data.task_id);
            setDriveStatus({ status: 'starting', message: 'Initializing...' });
        } catch (err) {
            alert("Failed to start import");
        }
    };

    const loadStats = async () => {
        try {
            const data = await getStats()
            setStats(data)
        } catch (err) {
            console.error('Failed to load stats:', err)
        }
    }

    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true)
        } else if (e.type === 'dragleave') {
            setDragActive(false)
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        const files = Array.from(e.dataTransfer.files).filter(file =>
            file.type.startsWith('image/')
        )
        setSelectedFiles(files)
    }

    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files)
        setSelectedFiles(files)
    }

    const handleUpload = async () => {
        if (selectedFiles.length === 0) return

        setUploading(true)
        setError(null)
        setResult(null)

        try {
            const data = await uploadBulkPhotos(selectedFiles)
            setResult(data)
            setSelectedFiles([])
            loadStats() // Refresh stats
        } catch (err) {
            setError(err.message)
        } finally {
            setUploading(false)
        }
    }

    const handleResetDatabase = async () => {
        // First confirmation
        const firstConfirm = window.confirm(
            '⚠️ WARNING: This will DELETE ALL photos and face data from the database!\n\n' +
            'This action CANNOT be undone.\n\n' +
            'Are you sure you want to continue?'
        )

        if (!firstConfirm) return

        // Second confirmation - must type DELETE
        const secondConfirm = window.prompt(
            'To confirm deletion, please type DELETE (in capital letters):'
        )

        if (secondConfirm !== 'DELETE') {
            alert('❌ Reset cancelled. You must type DELETE exactly to confirm.')
            return
        }

        // Proceed with reset
        setUploading(true)
        setError(null)
        setResult(null)

        try {
            await resetDatabase()
            alert('✅ Database reset successfully! All photos and face data have been deleted.')
            loadStats() // Refresh stats to show empty database
        } catch (err) {
            setError(err.message)
            alert('❌ Failed to reset database: ' + err.message)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="min-h-screen">
            {/* Premium Loading Overlay for Uploads */}
            {uploading && (
                <LoadingSpinner
                    message="Processing Your Photos"
                    tips={[
                        "💡 Our AI is detecting faces in your photos!",
                        "✨ Building searchable face embeddings...",
                        "🎯 Processing images with advanced AI...",
                        "🚀 Almost done! Indexing faces for fast search...",
                        "💜 Your photos will be ready in moments!"
                    ]}
                    fullScreen={true}
                />
            )}

            {/* Success Modal for Drive Import */}
            <SuccessModal
                isOpen={showSuccessModal}
                onClose={() => setShowSuccessModal(false)}
                title="Drive Import Complete!"
                message="🎉 All photos have been successfully imported from Google Drive and are ready to search!"
                autoClose={true}
                autoCloseDelay={5000}
            />

            <div className="max-w-7xl mx-auto px-6 py-12">
                {/* Drive Import Section */}
                <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl shadow-lg p-8 mb-8">
                    <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">☁️ Import from Google Drive</h2>
                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="Paste Public Drive Folder Link..."
                            className="flex-1 border border-purple-200 bg-white/50 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 text-slate-700"
                            value={driveUrl}
                            onChange={(e) => setDriveUrl(e.target.value)}
                        />
                        <button
                            onClick={handleDriveImport}
                            disabled={!!taskId && driveStatus?.status !== 'completed' && driveStatus?.status !== 'failed'}
                            className="bg-gradient-to-r from-purple-400 to-pink-400 text-white px-8 py-3 rounded-xl hover:scale-105 transition-transform disabled:opacity-50 font-semibold shadow-md"
                        >
                            {taskId && driveStatus?.status !== 'completed' && driveStatus?.status !== 'failed' ? 'Processing...' : 'Start Import'}
                        </button>
                    </div>

                    {driveStatus && (
                        <div className="mt-6">
                            <ProgressLoader
                                progress={driveStatus.progress && driveStatus.progress.includes('%') ? parseInt(driveStatus.progress) : 10}
                                total={100}
                                message={
                                    driveStatus.status === 'starting' ? '☁️ Starting Drive Import...' :
                                        driveStatus.status === 'processing' ? '☁️ Importing from Google Drive' :
                                            driveStatus.status === 'completed' ? '✅ Import Complete!' :
                                                driveStatus.status === 'failed' ? '❌ Import Failed' :
                                                    '☁️ Processing...'
                                }
                                status={driveStatus.status}
                                showPercentage={true}
                                showCount={false}
                            />
                            {driveStatus.message && driveStatus.status !== 'failed' && (
                                <p className="text-sm text-slate-600 mt-3 text-center">{driveStatus.message}</p>
                            )}
                            {driveStatus.error && (
                                <p className="text-sm text-red-600 mt-3 text-center font-medium">{driveStatus.error}</p>
                            )}
                        </div>
                    )}
                </div>

                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">Admin Panel</h1>
                    <p className="text-xl text-slate-600">Upload bulk photos to build the face database</p>
                </div>

                {/* Stats */}
                {stats && (
                    <>
                        <div className="grid md:grid-cols-2 gap-6 mb-8">
                            <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl p-8 shadow-lg">
                                <Database className="w-10 h-10 mb-3 text-purple-600" />
                                <div className="text-5xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">{stats.total_photos}</div>
                                <div className="text-slate-600 font-medium">Total Photos</div>
                            </div>
                            <div className="bg-white/60 backdrop-blur-md border border-pink-200/50 rounded-2xl p-8 shadow-lg">
                                <ImageIcon className="w-10 h-10 mb-3 text-pink-600" />
                                <div className="text-5xl font-bold mb-2 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">{stats.total_faces}</div>
                                <div className="text-slate-600 font-medium">Total Faces Indexed</div>
                            </div>
                        </div>
                    </>
                )}

                {/* Reset Database Button */}
                <div className="mb-8">
                    <button
                        onClick={handleResetDatabase}
                        disabled={uploading || !stats || stats.total_faces === 0}
                        className="w-full px-6 py-4 bg-red-500 text-white rounded-xl font-semibold hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 shadow-lg"
                    >
                        <Trash2 className="w-5 h-5" />
                        <span>🗑️ Reset Database (Delete All Photos & Faces)</span>
                    </button>
                    <p className="text-center text-slate-600 text-sm mt-3">
                        ⚠️ Use this after your event to clean up for the next event
                    </p>
                </div>


                {/* Upload Section */}
                <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl p-8 mb-8 shadow-lg">
                    <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Upload Photos</h2>

                    {/* Drag & Drop Area */}
                    <div
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${dragActive
                            ? 'border-purple-400 bg-purple-100/50'
                            : 'border-purple-200 hover:border-purple-300 bg-purple-50/30'
                            }`}
                    >
                        <input
                            type="file"
                            id="fileInput"
                            multiple
                            accept="image/*"
                            onChange={handleFileSelect}
                            className="hidden"
                        />

                        <label htmlFor="fileInput" className="cursor-pointer">
                            <Upload className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                            <div className="text-xl font-semibold text-slate-800 mb-2">
                                Click to select photos or drag & drop
                            </div>
                            <div className="text-slate-600">
                                Supports JPG, PNG, BMP, WEBP
                            </div>
                        </label>
                    </div>

                    {/* Selected Files */}
                    {selectedFiles.length > 0 && (
                        <div className="mt-6 bg-purple-50/50 backdrop-blur-sm rounded-xl p-5 border border-purple-100">
                            <div className="text-slate-800 font-semibold mb-3">
                                {selectedFiles.length} file(s) selected
                            </div>
                            <div className="max-h-40 overflow-y-auto space-y-1">
                                {selectedFiles.slice(0, 10).map((file, index) => (
                                    <div key={index} className="text-sm text-slate-600">
                                        • {file.name}
                                    </div>
                                ))}
                                {selectedFiles.length > 10 && (
                                    <div className="text-sm text-slate-600">
                                        ... and {selectedFiles.length - 10} more
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Upload Button */}
                    <button
                        onClick={handleUpload}
                        disabled={selectedFiles.length === 0 || uploading}
                        className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-purple-400 to-pink-400 text-white rounded-xl font-semibold hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 shadow-lg"
                    >
                        {uploading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <Upload className="w-5 h-5" />
                                <span>Upload Photos</span>
                            </>
                        )}
                    </button>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border border-red-300 rounded-xl p-5 mb-8 flex items-start space-x-3 shadow-sm">
                        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <div className="font-semibold text-red-700">Error</div>
                            <div className="text-red-600">{error}</div>
                        </div>
                    </div>
                )}

                {/* Success Result */}
                {result && (
                    <div className="bg-green-50 border border-green-300 rounded-xl p-6 mb-8 shadow-sm">
                        <div className="flex items-start space-x-3 mb-4">
                            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                            <div>
                                <div className="font-semibold text-green-700 text-lg">Upload Complete!</div>
                                <div className="text-green-600">
                                    {result.statistics.successful} photos processed successfully
                                    <br />
                                    {result.statistics.total_faces} faces detected and indexed
                                    {result.statistics.failed > 0 && (
                                        <><br />{result.statistics.failed} photos failed</>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Processing Details */}
                        <div className="mt-4">
                            <div className="font-semibold text-slate-800 mb-3">Processing Details</div>
                            <div className="max-h-60 overflow-y-auto space-y-2">
                                {result.statistics.photo_details.map((detail, index) => (
                                    <div
                                        key={index}
                                        className="bg-white/50 backdrop-blur-sm rounded-lg p-3 text-sm border border-purple-100"
                                    >
                                        <div className="font-semibold text-slate-800">{detail.filename}</div>
                                        {detail.success ? (
                                            <div className="text-green-600">
                                                ✓ {detail.faces_detected} faces detected
                                            </div>
                                        ) : (
                                            <div className="text-red-600">
                                                ✗ {detail.error}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Admin
