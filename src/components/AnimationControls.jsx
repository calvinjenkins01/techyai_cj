import React from 'react'
import { Sparkles, Trash2 } from 'lucide-react'

const ANIMATION_TYPES = {
  fadeIn: { label: 'Fade In', icon: '👁️' },
  fadeOut: { label: 'Fade Out', icon: '👻' },
  slideLeft: { label: 'Slide Left', icon: '←' },
  slideRight: { label: 'Slide Right', icon: '→' },
  slideUp: { label: 'Slide Up', icon: '↑' },
  slideDown: { label: 'Slide Down', icon: '↓' },
  zoomIn: { label: 'Zoom In', icon: '🔍' },
  zoomOut: { label: 'Zoom Out', icon: '🔍' },
  rotateClockwise: { label: 'Rotate CW', icon: '🔄' },
  rotateCounterClockwise: { label: 'Rotate CCW', icon: '🔄' },
  bounce: { label: 'Bounce', icon: '⛹️' },
  pulse: { label: 'Pulse', icon: '💓' },
}

export default function AnimationControls({ animations, onAnimationsChange, duration }) {
  const addAnimation = (type) => {
    const newAnimation = {
      id: Date.now(),
      type,
      startTime: 0,
      duration: 1,
      easing: 'ease-in-out',
    }
    onAnimationsChange([...animations, newAnimation])
  }

  const updateAnimation = (id, updates) => {
    onAnimationsChange(
      animations.map(anim =>
        anim.id === id ? { ...anim, ...updates } : anim
      )
    )
  }

  const removeAnimation = (id) => {
    onAnimationsChange(animations.filter(anim => anim.id !== id))
  }

  const easingOptions = [
    'linear',
    'ease-in',
    'ease-out',
    'ease-in-out',
    'ease-in-quad',
    'ease-out-quad',
  ]

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 space-y-6">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Sparkles size={20} /> Overlay Animations
      </h2>

      {/* Add Animation Buttons */}
      <div className="space-y-3">
        <p className="text-sm text-slate-300 font-medium">Add Animation</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {Object.entries(ANIMATION_TYPES).map(([key, { label, icon }]) => (
            <button
              key={key}
              onClick={() => addAnimation(key)}
              className="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded transition font-medium flex items-center gap-1 justify-center"
            >
              <span>{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Active Animations */}
      {animations.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-slate-300 font-medium">Active Animations</p>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {animations.map((anim) => (
              <div
                key={anim.id}
                className="bg-slate-700/50 rounded-lg p-4 space-y-3 border border-slate-600"
              >
                <div className="flex items-center justify-between">
                  <p className="font-medium text-sm">
                    {ANIMATION_TYPES[anim.type]?.label}
                  </p>
                  <button
                    onClick={() => removeAnimation(anim.id)}
                    className="text-red-400 hover:text-red-300 transition"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                {/* Start Time */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-slate-400">Start Time (s)</label>
                    <input
                      type="number"
                      min="0"
                      max={duration}
                      step="0.1"
                      value={anim.startTime.toFixed(1)}
                      onChange={(e) =>
                        updateAnimation(anim.id, {
                          startTime: parseFloat(e.target.value),
                        })
                      }
                      className="w-full bg-slate-600 rounded px-2 py-1 text-xs text-white border border-slate-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  {/* Duration */}
                  <div className="space-y-1">
                    <label className="text-xs text-slate-400">Duration (s)</label>
                    <input
                      type="number"
                      min="0.1"
                      max="10"
                      step="0.1"
                      value={anim.duration.toFixed(1)}
                      onChange={(e) =>
                        updateAnimation(anim.id, {
                          duration: parseFloat(e.target.value),
                        })
                      }
                      className="w-full bg-slate-600 rounded px-2 py-1 text-xs text-white border border-slate-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Easing */}
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Easing</label>
                  <select
                    value={anim.easing}
                    onChange={(e) =>
                      updateAnimation(anim.id, { easing: e.target.value })
                    }
                    className="w-full bg-slate-600 rounded px-2 py-1 text-xs text-white border border-slate-500 focus:border-blue-500 focus:outline-none"
                  >
                    {easingOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Timeline Preview */}
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Timeline</label>
                  <div className="flex h-6 bg-slate-600 rounded overflow-hidden relative">
                    <div
                      className="bg-blue-600/40 border-l-2 border-blue-400"
                      style={{
                        left: `${(anim.startTime / duration) * 100}%`,
                        width: `${(anim.duration / duration) * 100}%`,
                      }}
                    />
                    <span className="absolute inset-0 flex items-center px-2 text-xs text-white font-medium pointer-events-none">
                      {ANIMATION_TYPES[anim.type]?.label}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info */}
      <div className="bg-blue-900/20 border border-blue-800/50 rounded-lg p-3">
        <p className="text-xs text-blue-300">
          💡 Add animations to your overlay. They'll play during export. Combine multiple animations for complex effects!
        </p>
      </div>
    </div>
  )
}
