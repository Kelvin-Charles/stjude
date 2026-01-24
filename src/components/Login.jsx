import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(username, password)

    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error || 'Login failed')
    }

    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-600 flex items-center justify-center p-5">
      <div className="bg-white rounded-3xl p-10 shadow-2xl max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">ST Jude's Training</h1>
        <p className="text-gray-600 mb-8 text-center">Login to your account</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block mb-2 text-gray-700 font-medium">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block mb-2 text-gray-700 font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-100 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-3 rounded-xl text-lg font-bold transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/40 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-600 font-semibold hover:underline">
            Register here
          </Link>
        </p>

        <div className="mt-6 pt-6 border-t border-gray-100">
          <a 
            href="https://editor.raspberrypi.org/en/projects/blank-python-starter" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center justify-center w-full px-4 py-3 bg-pink-50 text-pink-600 rounded-xl font-semibold hover:bg-pink-100 transition-colors"
          >
            <span>🚀 Open Editor</span>
          </a>
        </div>
      </div>
    </div>
  )
}
