function DetailPanel({ location = null, onGetDirections }) {
  if (!location) return null

  const { name, category, description, image } = location.properties

  return (
    <div className="p-4 border-t border-gray-100">
      {image && (
        <img src={image} alt={name} className="w-full h-36 object-cover rounded-lg mb-3" />
      )}
      <h2 className="text-lg font-bold text-brand-primary">{name}</h2>
      <span className="inline-block text-xs font-medium text-white bg-brand-secondary px-2 py-0.5 rounded-full capitalize mt-1">
        {category}
      </span>
      {description && <p className="mt-2 text-sm text-gray-600 leading-relaxed">{description}</p>}
      <button
        onClick={() => onGetDirections && onGetDirections(location)}
        className="mt-4 w-full bg-brand-primary text-white text-sm font-semibold py-2 px-4 rounded-lg hover:bg-blue-800 transition-colors"
      >
        Get Directions
      </button>
    </div>
  )
}

export default DetailPanel
