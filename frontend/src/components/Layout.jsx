import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, ArrowLeftRight, Briefcase, LogOut, TrendingUp } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
  { to: '/positions', label: 'Positions', icon: Briefcase },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-950">
      <aside className="w-56 bg-slate-900 border-r border-slate-800 flex flex-col fixed h-full z-10">
        <div className="px-4 py-5 border-b border-slate-800 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-500" />
          <span className="font-semibold text-white text-sm">Portfolio Tracker</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-slate-800">
          <div className="px-3 py-1.5 text-xs text-slate-500 truncate mb-1">
            {user?.username}
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-white transition-colors w-full"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 ml-56">
        {children}
      </main>
    </div>
  )
}
