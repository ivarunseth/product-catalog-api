import React from 'react'
import { Link } from 'react-router-dom'

export default function ProductCard({ product }) {
  const firstImage =
    product.images?.length > 0
      ? product.images[0].src
      : '/placeholder.png' // fallback placeholder

  return (
    <Link
      to={`/product/${product.slug}`}
      className="block bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
    >
      <img
        src={firstImage}
        alt={product.title}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold truncate">{product.title}</h3>
        <p className="text-gray-600 text-sm line-clamp-2">{product.description}</p>
        <div className="mt-2 text-blue-600 font-bold">
          {product.currency} {product.price.toFixed(2)}
        </div>
      </div>
    </Link>
  )
}
