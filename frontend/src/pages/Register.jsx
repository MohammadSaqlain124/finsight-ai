import { Link } from 'react-router-dom'

function Register() {
  return (
    <main style={{ padding: '4rem' }}>
      <h1>Create account</h1>
      <p style={{ color: 'var(--ink-soft)' }}>Register form goes here.</p>
      <p>Already have an account? <Link to="/login">Sign in</Link></p>
    </main>
  )
}

export default Register