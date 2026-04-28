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
        aria-label="Search buildings, facilities"
        className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-brand-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:placeholder:text-slate-500"
      />
    </div>
  )
}

export default SearchBar
