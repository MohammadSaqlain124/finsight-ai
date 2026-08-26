import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Button from '../components/Button'

function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <main style={{ padding: '4rem', maxWidth: '900px' }}>
      <h1 style={{ fontSize: 'var(--text-2xl)' }}>Dashboard</h1>
      <p style={{ color: 'var(--ink-soft)', marginTop: '0.5rem' }}>
        Welcome{user ? `, ${user.full_name}` : ''}. Your financial overview will live here.
      </p>
      <div style={{ marginTop: '2rem' }}>
        <Button variant="secondary" onClick={handleLogout}>Sign out</Button>
      </div>
    </main>
  )
}

export default Dashboard