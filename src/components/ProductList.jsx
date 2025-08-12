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

  // Fetch products
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
          setFilters(data.filters)
        }
      })
      .catch(err => console.error(err))
  }, [page, debouncedQ, categoryId, brandId])

  return (
    <div>
      {/* Top Bar with Search & Filters */}
      <div className="flex flex-col md:flex-row items-center gap-4 mb-6 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        
        {/* Search Box */}
        <div className="relative flex-1">
          <input
            value={q}
            onChange={e => { setQ(e.target.value); setPage(1) }}
            placeholder="🔍 Search products..."
            className="w-full p-3 pr-10 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Category Filter */}
        <select
          value={categoryId}
          onChange={e => { setCategoryId(e.target.value); setPage(1) }}
          className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
          className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
      {items.length > 0 && (
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
      )}
    </div>
  )
}
