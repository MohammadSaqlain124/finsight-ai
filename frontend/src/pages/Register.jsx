import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import TextField from '../components/TextField'
import Button from '../components/Button'

function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    console.log('would register with:', { fullName, email, password })
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
        <Button type="submit" variant="primary">Create account</Button>
      </form>
    </AuthLayout>
  )
}

export default Register