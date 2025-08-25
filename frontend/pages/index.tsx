import Link from 'next/link';

export default function HomePage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#111827', marginBottom: '1rem' }}>
          SigmaSight
        </h1>
        <p style={{ fontSize: '1.25rem', color: '#6b7280', marginBottom: '2rem' }}>
          Portfolio Risk Management Platform
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
          <Link href="/chat" style={{
            display: 'block',
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: '500',
            transition: 'background-color 0.2s'
          }}>
            💬 Chat with GPT Portfolio Assistant
          </Link>
          <Link href="/portfolio" style={{
            display: 'block',
            backgroundColor: '#10b981',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            textDecoration: 'none',
            fontWeight: '500'
          }}>
            📊 View Demo Portfolios (Coming Soon)
          </Link>
        </div>
      </div>
    </div>
  );
}