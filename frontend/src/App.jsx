import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="flex h-screen items-center justify-center bg-gray-50">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-brand-primary">UniMap JJU</h1>
              <p className="mt-2 text-gray-500">Smart Campus Navigation — Coming Soon</p>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export default App
