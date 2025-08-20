import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Enable static export for Tauri desktop app
  output: 'export',

  // Disable image optimization for static export
  images: {
    unoptimized: true
  },

  // Use relative paths for assets (removed for static export)
  // assetPrefix: './',

  // Add trailing slash for better static file serving
  trailingSlash: true,

  // Disable ESLint during build for faster builds
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Disable server-side features not compatible with static export
  // experimental: {
  //   esmExternals: false
  // },

  // Configure for desktop app environment
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  }
}

export default nextConfig