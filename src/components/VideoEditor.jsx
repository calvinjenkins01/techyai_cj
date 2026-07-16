import React, { useState, useRef, useEffect } from 'react'
import { Upload, Download, Play, Pause, X } from 'lucide-react'
import Canvas from './Canvas'
import OverlayControls from './OverlayControls'
import AnimationControls from './AnimationControls'
import Timeline from './Timeline'
import ExportDialog from './ExportDialog'

export default function VideoEditor() {
  const [mainVideo, setMainVideo] = useState(null)
  const [overlayVideo, setOverlayVideo] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [showExport, setShowExport] = useState(false)

  const [overlay, setOverlay] = useState({
    x: 50,
    y: 50,
    width: 200,
    height: 150,
    opacity: 1,
    rotation: 0,
    borderRadius: 0,
    scale: 1,
  })
  const [animations, setAnimations] = useState([])

  const mainVideoRef = useRef(null)
  const overlayVideoRef = useRef(null)

  const handleMainVideoUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setMainVideo({ url, file })
    }
  }

  const handleOverlayUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setOverlayVideo({ url, file })
    }
  }

  const togglePlayPause = () => {
    if (mainVideoRef.current) {
      if (isPlaying) {
        mainVideoRef.current.pause()
      } else {
        mainVideoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleMainVideoMetadata = () => {
    if (mainVideoRef.current) {
      setDuration(mainVideoRef.current.duration)
    }
  }

  const handleTimeUpdate = () => {
    if (mainVideoRef.current) {
      setCurrentTime(mainVideoRef.current.currentTime)
      if (overlayVideoRef.current) {
        overlayVideoRef.current.currentTime = mainVideoRef.current.currentTime
      }
    }
  }

  const handleSeek = (time) => {
    if (mainVideoRef.current) {
      mainVideoRef.current.currentTime = time
      if (overlayVideoRef.current) {
        overlayVideoRef.current.currentTime = time
      }
      setCurrentTime(time)
    }
  }

  const handleOverlayChange = (updates) => {
    setOverlay(prev => ({ ...prev, ...updates }))
  }

  const clearOverlay = () => {
    setOverlayVideo(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="bg-slate-950 border-b border-slate-700 px-4 sm:px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">OverlayStudio</h1>
            <p className="text-slate-400 text-sm">Professional video overlay editor</p>
          </div>
          <button
            onClick={() => setShowExport(true)}
            disabled={!mainVideo}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 px-4 py-2 rounded-lg transition font-medium"
          >
            <Download size={20} /> Export
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6">
        {/* Upload Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Main Video Upload */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-slate-600 transition">
            <h2 className="text-lg font-semibold mb-4">Main Video (Your Talking Head)</h2>
            {!mainVideo ? (
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-slate-700/20 transition">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload size={32} className="text-slate-400 mb-2" />
                  <p className="text-sm text-slate-300">Upload main video</p>
                </div>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleMainVideoUpload}
                  className="hidden"
                />
              </label>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-slate-300">{mainVideo.file.name}</p>
                <button
                  onClick={() => setMainVideo(null)}
                  className="text-sm text-slate-400 hover:text-red-400 transition"
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Overlay Upload */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-slate-600 transition">
            <h2 className="text-lg font-semibold mb-4">Overlay (Article, Website, or Video)</h2>
            {!overlayVideo ? (
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-slate-700/20 transition">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload size={32} className="text-slate-400 mb-2" />
                  <p className="text-sm text-slate-300">Upload overlay video</p>
                </div>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleOverlayUpload}
                  className="hidden"
                />
              </label>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-slate-300">{overlayVideo.file.name}</p>
                <button
                  onClick={clearOverlay}
                  className="text-sm text-slate-400 hover:text-red-400 transition"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>

        {mainVideo && (
          <>
            {/* Video References (hidden) */}
            <video
              ref={mainVideoRef}
              src={mainVideo.url}
              onLoadedMetadata={handleMainVideoMetadata}
              onTimeUpdate={handleTimeUpdate}
              onEnded={() => setIsPlaying(false)}
              className="hidden"
            />
            {overlayVideo && (
              <video
                ref={overlayVideoRef}
                src={overlayVideo.url}
                className="hidden"
              />
            )}

            {/* Canvas Preview */}
            <Canvas
              mainVideoUrl={mainVideo.url}
              overlayVideoUrl={overlayVideo?.url}
              overlay={overlay}
              animations={animations}
              currentTime={currentTime}
            />

            {/* Controls */}
            <div className="bg-slate-800 rounded-xl p-4 sm:p-6 border border-slate-700 space-y-4">
              {/* Play/Pause */}
              <div className="flex items-center gap-4">
                <button
                  onClick={togglePlayPause}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition font-medium"
                >
                  {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
                <span className="text-sm text-slate-400">
                  {Math.floor(currentTime)}s / {Math.floor(duration)}s
                </span>
              </div>

              {/* Timeline */}
              <Timeline
                currentTime={currentTime}
                duration={duration}
                onSeek={handleSeek}
              />
            </div>

            {/* Overlay Controls */}
            {overlayVideo && (
              <>
                <OverlayControls overlay={overlay} onChange={handleOverlayChange} />
                <AnimationControls
                  animations={animations}
                  onAnimationsChange={setAnimations}
                  duration={duration}
                />
              </>
            )}
          </>
        )}
      </div>

      {/* Export Dialog */}
      {showExport && (
        <ExportDialog
          mainVideo={mainVideo}
          overlayVideo={overlayVideo}
          overlay={overlay}
          currentTime={currentTime}
          duration={duration}
          onClose={() => setShowExport(false)}
          mainVideoRef={mainVideoRef}
          overlayVideoRef={overlayVideoRef}
        />
      )}
    </div>
  )
}
