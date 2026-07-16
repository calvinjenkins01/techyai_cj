import React, { useRef, useEffect, useState } from 'react'

const EASING_FUNCTIONS = {
  linear: (t) => t,
  'ease-in': (t) => t * t,
  'ease-out': (t) => t * (2 - t),
  'ease-in-out': (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  'ease-in-quad': (t) => t * t,
  'ease-out-quad': (t) => t * (2 - t),
}

const getAnimationValue = (animations, currentTime, baseValue, animationType) => {
  let animatedValue = baseValue

  animations.forEach((anim) => {
    const animStart = anim.startTime
    const animEnd = anim.startTime + anim.duration

    if (currentTime >= animStart && currentTime <= animEnd) {
      const progress = (currentTime - animStart) / anim.duration
      const easedProgress = EASING_FUNCTIONS[anim.easing] ? EASING_FUNCTIONS[anim.easing](progress) : progress

      // Fade animations affect opacity
      if (animationType === 'opacity' && (anim.type === 'fadeIn' || anim.type === 'fadeOut')) {
        if (anim.type === 'fadeIn') animatedValue = baseValue * easedProgress
        if (anim.type === 'fadeOut') animatedValue = baseValue * (1 - easedProgress)
      }

      // Scale animations affect scale
      if (animationType === 'scale' && ['zoomIn', 'zoomOut', 'bounce', 'pulse'].includes(anim.type)) {
        if (anim.type === 'zoomIn') animatedValue = baseValue + (1 - baseValue) * easedProgress
        if (anim.type === 'zoomOut') animatedValue = baseValue - (baseValue - 0.5) * easedProgress
        if (anim.type === 'bounce') animatedValue = baseValue + Math.sin(easedProgress * Math.PI * 2) * 0.2
        if (anim.type === 'pulse') animatedValue = baseValue + Math.sin(easedProgress * Math.PI) * 0.15
      }

      // Rotation animations
      if (animationType === 'rotation' && ['rotateClockwise', 'rotateCounterClockwise'].includes(anim.type)) {
        if (anim.type === 'rotateClockwise') animatedValue = baseValue + 360 * easedProgress
        if (anim.type === 'rotateCounterClockwise') animatedValue = baseValue - 360 * easedProgress
      }

      // Slide animations (X position)
      if (animationType === 'x' && ['slideLeft', 'slideRight'].includes(anim.type)) {
        if (anim.type === 'slideLeft') animatedValue = baseValue - 50 * easedProgress
        if (anim.type === 'slideRight') animatedValue = baseValue + 50 * easedProgress
      }

      // Slide animations (Y position)
      if (animationType === 'y' && ['slideUp', 'slideDown'].includes(anim.type)) {
        if (anim.type === 'slideUp') animatedValue = baseValue - 50 * easedProgress
        if (anim.type === 'slideDown') animatedValue = baseValue + 50 * easedProgress
      }
    }
  })

  return animatedValue
}

export default function Canvas({ mainVideoUrl, overlayVideoUrl, overlay, animations = [], currentTime }) {
  const canvasRef = useRef(null)
  const mainVideoRef = useRef(null)
  const overlayVideoRef = useRef(null)
  const [videoDimensions, setVideoDimensions] = useState({ width: 1280, height: 720 })

  const CANVAS_WIDTH = Math.min(window.innerWidth - 48, 960)
  const CANVAS_HEIGHT = (CANVAS_WIDTH / 16) * 9

  useEffect(() => {
    if (!mainVideoRef.current) {
      mainVideoRef.current = new Image()
    }
    mainVideoRef.current.src = mainVideoUrl
    mainVideoRef.current.onloadedmetadata = () => {
      if (mainVideoRef.current instanceof HTMLVideoElement) {
        setVideoDimensions({
          width: mainVideoRef.current.videoWidth,
          height: mainVideoRef.current.videoHeight,
        })
      }
    }
  }, [mainVideoUrl])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const drawFrame = () => {
      const scaleX = CANVAS_WIDTH / videoDimensions.width
      const scaleY = CANVAS_HEIGHT / videoDimensions.height
      const scale = Math.min(scaleX, scaleY)

      const scaledWidth = videoDimensions.width * scale
      const scaledHeight = videoDimensions.height * scale
      const offsetX = (CANVAS_WIDTH - scaledWidth) / 2
      const offsetY = (CANVAS_HEIGHT - scaledHeight) / 2

      // Clear canvas
      ctx.fillStyle = '#000'
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

      // Draw main video
      const mainVideo = document.querySelector('video[style*="none"]')
      if (mainVideo && mainVideo.readyState === mainVideo.HAVE_ENOUGH_DATA) {
        ctx.drawImage(mainVideo, offsetX, offsetY, scaledWidth, scaledHeight)
      }

      // Draw overlay with animations
      if (overlayVideoUrl) {
        const overlayVideo = document.querySelectorAll('video')[1]
        if (overlayVideo && overlayVideo.readyState === overlayVideo.HAVE_ENOUGH_DATA) {
          ctx.save()

          // Apply animations
          const animatedX = getAnimationValue(animations, currentTime, overlay.x, 'x')
          const animatedY = getAnimationValue(animations, currentTime, overlay.y, 'y')
          const animatedOpacity = getAnimationValue(animations, currentTime, overlay.opacity, 'opacity')
          const animatedRotation = getAnimationValue(animations, currentTime, overlay.rotation, 'rotation')
          const animatedScale = getAnimationValue(animations, currentTime, overlay.scale, 'scale')

          const overlayX = (animatedX / 100) * CANVAS_WIDTH
          const overlayY = (animatedY / 100) * CANVAS_HEIGHT
          const overlayWidth = overlay.width
          const overlayHeight = overlay.height

          ctx.globalAlpha = animatedOpacity
          ctx.translate(overlayX + overlayWidth / 2, overlayY + overlayHeight / 2)
          ctx.rotate((animatedRotation * Math.PI) / 180)
          ctx.scale(animatedScale, animatedScale)

          ctx.beginPath()
          ctx.roundRect(
            -overlayWidth / 2,
            -overlayHeight / 2,
            overlayWidth,
            overlayHeight,
            overlay.borderRadius
          )
          ctx.clip()

          ctx.drawImage(
            overlayVideo,
            -overlayWidth / 2,
            -overlayHeight / 2,
            overlayWidth,
            overlayHeight
          )

          ctx.restore()
        }
      }
    }

    drawFrame()
  }, [currentTime, overlayVideoUrl, overlay, animations, CANVAS_WIDTH, videoDimensions])

  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700">
      <div className="flex justify-center bg-black p-4 sm:p-6">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="w-full max-w-full rounded-lg shadow-2xl"
          style={{ maxHeight: '70vh' }}
        />
      </div>
    </div>
  )
}
