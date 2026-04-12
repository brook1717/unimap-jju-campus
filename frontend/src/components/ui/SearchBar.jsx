import { useState } from 'react'

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('')

  const handleChange = (e) => {
    setQuery(e.target.value)
    onSearch && onSearch(e.target.value)
  }

  return (
    <div className="p-4">
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder="Search buildings, facilities..."
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-primary text-sm"
      />
    </div>
  )
}

export default SearchBar
