import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import TextField from '../components/TextField'
import Button from '../components/Button'
import { apiFetch } from '../lib/api'

function Register() {
  const [fullName, setFullName] = useState('')
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
      await apiFetch('/api/auth/register', {
        method: 'POST',
        body: { full_name: fullName, email, password },
      })
      navigate('/login')  // account created — send them to sign in
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Create account"
      subtitle="Start making sense of your money."
      footer={<>Already have an account? <Link to="/login">Sign in</Link></>}
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <TextField label="Full name" id="fullName" type="text" value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Jane Doe" autoComplete="name" required />
        <TextField label="Email" id="email" type="email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com" autoComplete="email" required />
        <TextField label="Password" id="password" type="password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="At least 8 characters" autoComplete="new-password" required minLength={8} />

        {error && (
          <p style={{ color: 'var(--ledger-red)', fontSize: 'var(--text-sm)', margin: 0 }}>
            {error}
          </p>
        )}

        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'Creating account…' : 'Create account'}
        </Button>
      </form>
    </AuthLayout>
  )
}

export default Register