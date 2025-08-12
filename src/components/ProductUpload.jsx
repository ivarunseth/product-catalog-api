import React, { useState } from 'react'

export default function ProductUpload() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [currency, setCurrency] = useState('INR')
  const [brand, setBrand] = useState('') // text instead of brand_id
  const [categories, setCategories] = useState('') // comma-separated
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  // Handle file uploads & convert to base64
  const handleImageUpload = (e) => {
    const files = e.target.files
    const readers = []
    for (let file of files) {
      readers.push(
        new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = () => resolve({ data: reader.result.split(',')[1], mime_type: file.type })
          reader.onerror = reject
          reader.readAsDataURL(file)
        })
      )
    }
    Promise.all(readers).then(results => {
      setImages(prev => [...prev, ...results])
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const payload = {
      title,
      description,
      price: parseFloat(price),
      currency,
      brand_id: brand || null,
      category_ids: categories
        ? categories.split(',').map(c => c.trim())
        : [],
      images
    }

    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (res.ok) {
        setMessage('✅ Product created successfully!')
        setTitle('')
        setDescription('')
        setPrice('')
        setCurrency('INR')
        setBrand('')
        setCategories('')
        setImages([])
      } else {
        setMessage(`❌ ${data.error || 'Failed to create product'}`)
      }
    } catch (err) {
      setMessage(`❌ ${err.message}`)
    }

    setLoading(false)
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 className="text-2xl font-bold mb-6">Create New Product</h2>

      {message && <p className="mb-4 text-sm font-medium">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block mb-1 font-medium">Title *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full p-2 border rounded-lg"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block mb-1 font-medium">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="4"
            className="w-full p-2 border rounded-lg"
          />
        </div>

        {/* Price & Currency */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block mb-1 font-medium">Price *</label>
            <input
              type="number"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              className="w-full p-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Currency</label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full p-2 border rounded-lg"
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="INR">INR</option>
            </select>
          </div>
        </div>

        {/* Brand (Text Field) */}
        <div>
          <label className="block mb-1 font-medium">Brand</label>
          <input
            type="text"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            className="w-full p-2 border rounded-lg"
          />
        </div>

        {/* Categories (comma separated text input) */}
        <div>
          <label className="block mb-1 font-medium">Categories (comma separated IDs)</label>
          <input
            type="text"
            value={categories}
            onChange={(e) => setCategories(e.target.value)}
            placeholder="e.g., 1, 2, 3"
            className="w-full p-2 border rounded-lg"
          />
        </div>

        {/* Images */}
        <div>
          <label className="block mb-1 font-medium">Images</label>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleImageUpload}
            className="w-full"
          />
          {images.length > 0 && (
            <div className="grid grid-cols-3 gap-4 mt-2">
              {images.map((img, i) => (
                <img
                  key={i}
                  src={`data:${img.mime_type};base64,${img.data}`}
                  alt={`Preview ${i}`}
                  className="w-full h-24 object-cover rounded"
                />
              ))}
            </div>
          )}
        </div>

        {/* Submit */}
        <div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Create Product'}
          </button>
        </div>
      </form>
    </div>
  )
}
