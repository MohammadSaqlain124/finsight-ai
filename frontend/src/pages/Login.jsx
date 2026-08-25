import { useState } from 'react'
import { Link } from 'react-router-dom'
import TextField from '../components/TextField'
import Button from '../components/Button'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    console.log('would sign in with:', { email, password })
  }

  return (
    <main style={{ padding: '4rem', maxWidth: '380px' }}>
      <h1 style={{ fontSize: 'var(--text-2xl)' }}>Sign in</h1>
      <p style={{ color: 'var(--ink-soft)', marginTop: '0.5rem' }}>
        Welcome back to FinSight AI.
      </p>

      <form onSubmit={handleSubmit} style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <TextField
          label="Email" id="email" type="email"
          value={email} onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com" autoComplete="email" required
        />
        <TextField
          label="Password" id="password" type="password"
          value={password} onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••" autoComplete="current-password" required
        />
        <Button type="submit" variant="primary">Sign in</Button>
      </form>

      <p style={{ marginTop: '2rem', color: 'var(--ink-soft)' }}>
        New here? <Link to="/register">Create an account</Link>
      </p>
    </main>
  )
}

export default Login