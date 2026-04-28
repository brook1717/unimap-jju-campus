import { useState } from 'react'
import { MapPin } from 'lucide-react'

function DetailPanel({ location = null, onGetDirections }) {
  const [imgError, setImgError] = useState(false)

  if (!location) return null

  const { name, category, description, image } = location.properties
  const hasImage = !!image && !imgError

  return (
    <div className="p-4 border-t border-slate-100 dark:border-slate-800">
      {hasImage ? (
        <img
          src={image}
          alt={name}
          className="w-full h-36 object-cover rounded-lg mb-3"
          onError={() => setImgError(true)}
        />
      ) : (
        <div className="flex h-36 w-full items-center justify-center rounded-lg mb-3 bg-gradient-to-br from-slate-100 via-slate-200 to-slate-300 dark:from-slate-800 dark:via-slate-750 dark:to-slate-700">
          <MapPin className="h-8 w-8 text-slate-400/60 dark:text-slate-500/60" />
        </div>
      )}
      <h2 className="text-lg font-bold text-brand-primary dark:text-brand-primary">{name}</h2>
      <span className="inline-block text-xs font-medium text-white bg-brand-secondary px-2 py-0.5 rounded-full capitalize mt-1">
        {category}
      </span>
      {description && <p className="mt-2 text-sm text-slate-600 leading-relaxed dark:text-slate-400">{description}</p>}
      <button
        onClick={() => onGetDirections && onGetDirections(location)}
        className="mt-4 w-full bg-brand-primary text-white text-sm font-semibold py-2 px-4 rounded-lg hover:bg-brand-primary/90 transition-colors"
      >
        Get Directions
      </button>
    </div>
  )
}

export default DetailPanel
