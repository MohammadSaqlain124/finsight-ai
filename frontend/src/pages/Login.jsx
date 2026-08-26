import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import TextField from '../components/TextField'
import Button from '../components/Button'
import { apiFetch } from '../lib/api'
import { saveToken } from '../lib/auth'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await apiFetch('/api/auth/login', {
        method: 'POST',
        form: { username: email, password },   // OAuth2 field is "username"; we pass the email
      })
      saveToken(data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Sign in"
      subtitle="Welcome back to FinSight AI."
      footer={<>New here? <Link to="/register">Create an account</Link></>}
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <TextField label="Email" id="email" type="email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com" autoComplete="email" required />
        <TextField label="Password" id="password" type="password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••" autoComplete="current-password" required />

        {error && (
          <p style={{ color: 'var(--ledger-red)', fontSize: 'var(--text-sm)', margin: 0 }}>
            {error}
          </p>
        )}

        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>
    </AuthLayout>
  )
}

export default Login