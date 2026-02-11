import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import StudentDashboard from './StudentDashboard'
import MentorDashboard from './MentorDashboard'
import ManagerDashboard from './ManagerDashboard'
import NotificationCenter from './NotificationCenter'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function Dashboard() {
  const { user, logout, token } = useAuth()

  if (!user) {
    return null
  }

  const getDashboardComponent = () => {
    switch (user.role) {
      case 'student':
        return <StudentDashboard />
      case 'mentor':
        return <MentorDashboard />
      case 'manager':
        return <ManagerDashboard />
      default:
        return <div>Unknown role</div>
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-600">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-800">ST Jude's Training</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                Welcome, <span className="font-semibold">{user.full_name}</span> ({user.role})
              </span>
              <NotificationCenter />
              <button
                onClick={logout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {getDashboardComponent()}
      </div>
    </div>
  )
}
