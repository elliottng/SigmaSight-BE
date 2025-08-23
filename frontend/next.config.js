/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['assets.sigmasight.com'],
    unoptimized: true
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  env: {
    API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
    AUTH_ENABLED: process.env.NEXT_PUBLIC_AUTH_ENABLED || 'false',
    DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE || 'false'
  }
}

module.exports = nextConfig