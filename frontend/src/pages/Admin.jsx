import React, { useState, useEffect } from 'react'
import { Upload, Image as ImageIcon, AlertCircle, CheckCircle, Database, Trash2 } from 'lucide-react'
import { uploadBulkPhotos, getStats, resetDatabase } from '../services/api'

const Admin = () => {
    const [selectedFiles, setSelectedFiles] = useState([])
    const [uploading, setUploading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [stats, setStats] = useState(null)
    const [dragActive, setDragActive] = useState(false)

    // Load stats on mount
    const [driveUrl, setDriveUrl] = useState('');
    const [taskId, setTaskId] = useState(null);
    const [driveStatus, setDriveStatus] = useState(null);

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

                        // Only show alert once per task
                        if (data.status === 'completed' && !alertShownRef.current) {
                            alertShownRef.current = true;
                            alert("Drive Import Complete!");
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Drive Import Section */}
            <div className="bg-white rounded-lg shadow p-6 mb-8 border border-blue-100">
                <h2 className="text-xl font-semibold mb-4 text-slate-800">☁️ Import from Google Drive</h2>
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Paste Public Drive Folder Link..."
                        className="flex-1 border p-2 rounded"
                        value={driveUrl}
                        onChange={(e) => setDriveUrl(e.target.value)}
                    />
                    <button
                        onClick={handleDriveImport}
                        disabled={!!taskId && driveStatus?.status !== 'completed' && driveStatus?.status !== 'failed'}
                        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {taskId && driveStatus?.status !== 'completed' && driveStatus?.status !== 'failed' ? 'Processing...' : 'Start Import'}
                    </button>
                </div>

                {driveStatus && (
                    <div className="mt-4 p-4 bg-slate-50 rounded">
                        <div className="flex justify-between mb-2">
                            <span className="font-medium capitalize">{driveStatus.status}</span>
                            <span>{driveStatus.progress}</span>
                        </div>
                        <div className="text-sm text-slate-500">{driveStatus.message || driveStatus.error}</div>
                        {driveStatus.status === 'processing' && (
                            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                                <div
                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                                    style={{ width: driveStatus.progress && driveStatus.progress.includes('%') ? driveStatus.progress : '10%' }}
                                ></div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="bg-white rounded-lg shadow-xl overflow-hidden min-h-[500px] flex flex-col">
                <div className="p-8 border-b border-slate-100">
                    <h1 className="text-3xl font-bold text-slate-900">Upload Event Photos</h1>
                    <p className="mt-2 text-slate-500">Drag and drop photos or select files</p>
                </div>

                {/* The original content of the return statement starts here, but with a new outer div */}
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-bold text-white mb-4">Admin Panel</h1>
                    <p className="text-xl text-slate-300">Upload bulk photos to build the face database</p>
                </div>

                {/* Stats */}
                {stats && (
                    <>
                        <div className="grid md:grid-cols-2 gap-6 mb-8">
                            <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-2xl p-6 text-white">
                                <Database className="w-8 h-8 mb-2 opacity-80" />
                                <div className="text-4xl font-bold mb-1">{stats.total_photos}</div>
                                <div className="text-indigo-200">Total Photos</div>
                            </div>
                            <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl p-6 text-white">
                                <ImageIcon className="w-8 h-8 mb-2 opacity-80" />
                                <div className="text-4xl font-bold mb-1">{stats.total_faces}</div>
                                <div className="text-purple-200">Total Faces Indexed</div>
                            </div>
                        </div>

                        {/* Reset Database Button */}
                        <div className="mb-8">
                            <button
                                onClick={handleResetDatabase}
                                disabled={uploading || stats.total_faces === 0}
                                className="w-full px-6 py-4 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 border-2 border-red-500"
                            >
                                <Trash2 className="w-5 h-5" />
                                <span>🗑️ Reset Database (Delete All Photos & Faces)</span>
                            </button>
                            <p className="text-center text-slate-400 text-sm mt-2">
                                ⚠️ Use this after your event to clean up for the next event
                            </p>
                        </div>
                    </>
                )}

                {/* Upload Section */}
                <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 mb-8">
                    <h2 className="text-2xl font-bold text-white mb-6">Upload Photos</h2>

                    {/* Drag & Drop Area */}
                    <div
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${dragActive
                            ? 'border-indigo-500 bg-indigo-500/10'
                            : 'border-slate-600 hover:border-slate-500'
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
                            <Upload className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                            <div className="text-xl font-semibold text-white mb-2">
                                Click to select photos or drag & drop
                            </div>
                            <div className="text-slate-400">
                                Supports JPG, PNG, BMP, WEBP
                            </div>
                        </label>
                    </div>

                    {/* Selected Files */}
                    {selectedFiles.length > 0 && (
                        <div className="mt-6 bg-slate-900/50 rounded-lg p-4">
                            <div className="text-white font-semibold mb-2">
                                {selectedFiles.length} file(s) selected
                            </div>
                            <div className="max-h-40 overflow-y-auto space-y-1">
                                {selectedFiles.slice(0, 10).map((file, index) => (
                                    <div key={index} className="text-sm text-slate-400">
                                        • {file.name}
                                    </div>
                                ))}
                                {selectedFiles.length > 10 && (
                                    <div className="text-sm text-slate-500">
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
                        className="w-full mt-6 px-6 py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
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
                    <div className="bg-red-500/10 border border-red-500 rounded-xl p-4 mb-8 flex items-start space-x-3">
                        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <div className="font-semibold text-red-500">Error</div>
                            <div className="text-red-400">{error}</div>
                        </div>
                    </div>
                )}

                {/* Success Result */}
                {result && (
                    <div className="bg-green-500/10 border border-green-500 rounded-xl p-6 mb-8">
                        <div className="flex items-start space-x-3 mb-4">
                            <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                            <div>
                                <div className="font-semibold text-green-500 text-lg">Upload Complete!</div>
                                <div className="text-green-400">
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
                            <div className="font-semibold text-white mb-2">Processing Details</div>
                            <div className="max-h-60 overflow-y-auto space-y-2">
                                {result.statistics.photo_details.map((detail, index) => (
                                    <div
                                        key={index}
                                        className="bg-slate-900/50 rounded-lg p-3 text-sm"
                                    >
                                        <div className="font-semibold text-white">{detail.filename}</div>
                                        {detail.success ? (
                                            <div className="text-green-400">
                                                ✓ {detail.faces_detected} faces detected
                                            </div>
                                        ) : (
                                            <div className="text-red-400">
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
