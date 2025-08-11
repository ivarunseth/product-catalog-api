import React, { useState, useEffect } from 'react'
import ProductCard from './ProductCard'

export default function ProductList() {
  const [items, setItems] = useState([])
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const [debouncedQ, setDebouncedQ] = useState(q)

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQ(q)
    }, 500) // delay in ms

    return () => {
      clearTimeout(handler)
    }
  }, [q])

  // Fetch products when page or debounced search changes
  useEffect(() => {
    const params = new URLSearchParams({ q: debouncedQ, page })
    fetch('/api/products/search?' + params.toString())
      .then(r => r.json())
      .then(data => { setItems(data.items || []) })
      .catch(err => console.error(err))
  }, [page, debouncedQ])

  return (
    <div>
      <div className="mb-6 flex justify-center">
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Search products..."
          className="w-full max-w-lg p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {items.map(item => <ProductCard key={item.id} product={item} />)}
      </div>
      <div className="mt-8 flex justify-center space-x-4">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm font-medium"
        >
          Prev
        </button>
        <button
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm font-medium"
        >
          Next
        </button>
      </div>
    </div>
  )
}
