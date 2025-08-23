/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['assets.sigmasight.com'],
    unoptimized: true
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  experimental: {
    optimizeCss: true,
    optimizeImages: true
  },
  env: {
    API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
    AUTH_ENABLED: process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true',
    DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE === 'true'
  }
}

module.exports = nextConfig