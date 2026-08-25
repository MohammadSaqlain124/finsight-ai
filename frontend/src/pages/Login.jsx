import { Link } from 'react-router-dom'

function Login() {
  return (
    <main style={{ padding: '4rem' }}>
      <h1>Sign in</h1>
      <p style={{ color: 'var(--ink-soft)' }}>Login form goes here.</p>
      <p>New here? <Link to="/register">Create an account</Link></p>
    </main>
  )
}

export default Login