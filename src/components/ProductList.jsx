import React, { useState, useEffect } from 'react'
import ProductCard from './ProductCard'

export default function ProductList() {
  const [items, setItems] = useState([])
  const [filters, setFilters] = useState({ categories: [], brands: [] })
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [brandId, setBrandId] = useState('')
  const [debouncedQ, setDebouncedQ] = useState(q)

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQ(q)
    }, 500)
    return () => clearTimeout(handler)
  }, [q])

  // Fetch products when filters or page change
  useEffect(() => {
    const params = new URLSearchParams({
      q: debouncedQ,
      page,
      ...(categoryId ? { category_id: categoryId } : {}),
      ...(brandId ? { brand_id: brandId } : {})
    })

    fetch('/api/products/search?' + params.toString())
      .then(r => r.json())
      .then(data => {
        setItems(data.items || [])
        if (data.filters) {
          setFilters(data.filters) // categories & brands from backend
        }
      })
      .catch(err => console.error(err))
  }, [page, debouncedQ, categoryId, brandId])

  return (
    <div>
      {/* Search Bar */}
      <div className="mb-6 flex justify-center">
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Search products..."
          className="w-full max-w-lg p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4 justify-center">
        {/* Category Filter */}
        <select
          value={categoryId}
          onChange={e => { setCategoryId(e.target.value); setPage(1) }}
          className="p-2 border border-gray-300 rounded-lg"
        >
          <option value="">All Categories</option>
          {filters.categories.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        {/* Brand Filter */}
        <select
          value={brandId}
          onChange={e => { setBrandId(e.target.value); setPage(1) }}
          className="p-2 border border-gray-300 rounded-lg"
        >
          <option value="">All Brands</option>
          {filters.brands.map(b => (
            <option key={b.id} value={b.id}>{b.name}</option>
          ))}
        </select>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {items.map(item => <ProductCard key={item.id} product={item} />)}
      </div>

      {/* Pagination */}
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
