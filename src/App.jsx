import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export default function App(){
  return (
    <div className='min-h-screen flex flex-col bg-gray-50'>
      <header className='bg-white shadow sticky top-0 z-10'>
        <div className='max-w-7xl mx-auto px-4 py-4 flex items-center justify-between'>
          <Link to='/' className='text-xl font-bold text-blue-600 hover:text-blue-800 transition'>Product Catalog</Link>
        </div>
      </header>
      <main className='flex-1 max-w-7xl mx-auto p-4 w-full'>
        <Outlet />
      </main>
      <footer className='bg-white border-t mt-8'>
        <div className='max-w-7xl mx-auto px-4 py-6 text-sm text-gray-500'>
          © 2025 Product Catalog. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
