function Sidebar({ children }) {
  return (
    <>
      {/* Desktop: fixed left sidebar */}
      <aside className="hidden md:flex md:flex-col md:w-80 md:h-full bg-white shadow-lg z-10 overflow-y-auto">
        {children}
      </aside>

      {/* Mobile: bottom sheet */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl z-10 max-h-[50vh] overflow-y-auto">
        <div className="mx-auto mt-2 mb-1 h-1 w-10 rounded-full bg-gray-300" />
        {children}
      </div>
    </>
  )
}

export default Sidebar
