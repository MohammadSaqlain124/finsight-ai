import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) return null            // still checking the token — wait, don't redirect
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children                     // authenticated — render the page
}