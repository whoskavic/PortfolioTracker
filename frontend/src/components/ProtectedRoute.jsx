import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950">
        <span className="text-slate-400 text-sm">Loading...</span>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}
