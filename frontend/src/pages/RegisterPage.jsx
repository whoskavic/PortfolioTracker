import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TrendingUp } from 'lucide-react'
import client from '../api/client'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await client.post('/register', form)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <TrendingUp className="w-6 h-6 text-blue-500" />
          <span className="text-xl font-bold text-white">Portfolio Tracker</span>
        </div>

        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
          <h1 className="text-lg font-semibold text-white mb-6">Create account</h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Username</label>
              <input
                type="text"
                value={form.username}
                onChange={e => setForm(p => ({ ...p, username: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                placeholder="username"
                required
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Password</label>
              <input
                type="password"
                value={form.password}
                onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                placeholder="••••••••"
                required
              />
            </div>

            {error && <p className="text-red-400 text-xs">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition-colors"
            >
              {loading ? 'Creating...' : 'Create account'}
            </button>
          </form>

          <p className="text-center text-xs text-slate-500 mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-400 hover:text-blue-300">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
