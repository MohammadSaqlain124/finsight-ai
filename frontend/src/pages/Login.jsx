import { Link } from 'react-router-dom'
import Button from '../components/Button'

function Login() {
  return (
    <main style={{ padding: '4rem', maxWidth: '400px' }}>
      <h1 style={{ fontSize: 'var(--text-2xl)' }}>Sign in</h1>
      <p style={{ color: 'var(--ink-soft)', marginTop: '0.5rem' }}>
        Welcome back to FinSight AI.
      </p>

      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <Button variant="primary">Sign in</Button>
        <Button variant="secondary" disabled>Disabled</Button>
      </div>

      <p style={{ marginTop: '2rem', color: 'var(--ink-soft)' }}>
        New here? <Link to="/register">Create an account</Link>
      </p>
    </main>
  )
}

export default Login