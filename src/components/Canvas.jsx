import React, { useRef, useEffect, useState } from 'react'

export default function Canvas({ mainVideoUrl, overlayVideoUrl, overlay, animations = [], currentTime }) {
  const canvasRef = useRef(null)
  const mainVideoRef = useRef(null)
  const overlayVideoRef = useRef(null)

  useEffect(() => {
    if (!mainVideoRef.current) {
      mainVideoRef.current = document.createElement('video')
      mainVideoRef.current.crossOrigin = 'anonymous'
    }
    mainVideoRef.current.src = mainVideoUrl
  }, [mainVideoUrl])

  useEffect(() => {
    if (!overlayVideoRef.current && overlayVideoUrl) {
      overlayVideoRef.current = document.createElement('video')
      overlayVideoRef.current.crossOrigin = 'anonymous'
    }
    if (overlayVideoRef.current) {
      overlayVideoRef.current.src = overlayVideoUrl
    }
  }, [overlayVideoUrl])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const animate = () => {
      if (mainVideoRef.current && mainVideoRef.current.readyState >= 2) {
        ctx.fillStyle = '#000000'
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        const video = mainVideoRef.current
        const hRatio = canvas.width / video.videoWidth
        const vRatio = canvas.height / video.videoHeight
        const ratio = Math.min(hRatio, vRatio)

        const centerShift_x = (canvas.width - video.videoWidth * ratio) / 2
        const centerShift_y = (canvas.height - video.videoHeight * ratio) / 2

        ctx.drawImage(
          video,
          centerShift_x,
          centerShift_y,
          video.videoWidth * ratio,
          video.videoHeight * ratio
        )

        // Draw overlay if available
        if (overlayVideoUrl && overlayVideoRef.current && overlayVideoRef.current.readyState >= 2) {
          ctx.save()

          const overlayX = (overlay.x / 100) * canvas.width
          const overlayY = (overlay.y / 100) * canvas.height
          const overlayWidth = overlay.width
          const overlayHeight = overlay.height

          ctx.globalAlpha = overlay.opacity
          ctx.translate(overlayX + overlayWidth / 2, overlayY + overlayHeight / 2)
          ctx.rotate((overlay.rotation * Math.PI) / 180)
          ctx.scale(overlay.scale, overlay.scale)

          ctx.fillStyle = 'rgba(0,0,0,0.1)'
          ctx.fillRect(-overlayWidth / 2, -overlayHeight / 2, overlayWidth, overlayHeight)

          try {
            ctx.drawImage(
              overlayVideoRef.current,
              -overlayWidth / 2,
              -overlayHeight / 2,
              overlayWidth,
              overlayHeight
            )
          } catch (e) {
            // Overlay not ready yet
          }

          ctx.restore()
        }
      }
    }

    animate()
  }, [currentTime, overlayVideoUrl, overlay])

  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700">
      <div className="flex justify-center bg-black p-4 sm:p-6">
        <canvas
          ref={canvasRef}
          width={960}
          height={540}
          className="w-full max-w-full rounded-lg shadow-2xl"
          style={{ maxHeight: '70vh', display: 'block' }}
        />
      </div>
    </div>
  )
}
