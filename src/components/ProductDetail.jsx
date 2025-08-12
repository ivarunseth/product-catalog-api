import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

export default function ProductDetail() {
  const { slug } = useParams()
  const [p, setP] = useState(null)

  useEffect(() => {
    fetch(`/api/products/${slug}`)
      .then(r => r.json())
      .then(setP)
      .catch(() => setP(null))
  }, [slug])

  if (p === null) return <div>Loading...</div>
  if (!p) return <div>Product not found.</div>

  return (
    <div>
      <nav className='text-sm text-gray-600 mb-3'>
        {p.breadcrumb && p.breadcrumb.map((b, i) =>
          <span key={b.id}>
            {b.name}{i < p.breadcrumb.length - 1 ? ' > ' : ''}
          </span>
        )}
      </nav>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        <div className='md:col-span-2 flex items-center justify-center bg-gray-100 rounded'>
          <img
            src={p.images?.[0]?.src || '/placeholder.png'}
            alt={p.title}
            className="max-h-[500px] w-auto object-contain"
          />
        </div>
        <div>
          <h1 className='text-2xl font-bold'>{p.title}</h1>
          <div className='text-2xl text-green-600 mt-2'>
            ${(p.price || 0).toFixed(2)}
          </div>
          <div className='mt-4 text-gray-700'>{p.description}</div>
          <div className='mt-4 text-sm text-gray-600'>
            Brand: {p.brand?.name}
          </div>
          <div className='mt-4'>
            <Link to='/' className='text-blue-600 hover:underline'>Back to products</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
