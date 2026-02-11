import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function NotificationCenter() {
  const { token, user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    if (user && user.role === 'student') {
      fetchUnreadCount()
      fetchNotifications()
      // Poll for new notifications every 10 seconds
      const interval = setInterval(() => {
        fetchUnreadCount()
        fetchNotifications()
      }, 10000)
      return () => clearInterval(interval)
    }
  }, [user, token])

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_URL}/api/notifications?limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setNotifications(data.notifications || [])
      }
    } catch (error) {
      console.error('Error fetching notifications:', error)
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(`${API_URL}/api/notifications/unread-count`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setUnreadCount(data.count || 0)
      }
    } catch (error) {
      console.error('Error fetching unread count:', error)
    }
  }

  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(`${API_URL}/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        setNotifications(notifications.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        ))
        setUnreadCount(Math.max(0, unreadCount - 1))
      }
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      const response = await fetch(`${API_URL}/api/notifications/mark-all-read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        setNotifications(notifications.map(n => ({ ...n, is_read: true })))
        setUnreadCount(0)
      }
    } catch (error) {
      console.error('Error marking all as read:', error)
    }
  }

  const handleNotificationClick = (notification) => {
    if (!notification.is_read) {
      markAsRead(notification.id)
    }
    setIsOpen(false)
    // You can add navigation logic here based on notification.related_type
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
  }

  // Only show for students
  if (!user || user.role !== 'student') {
    return null
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-700 hover:text-indigo-600 transition-colors"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50 border border-gray-200 max-h-96 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-bold text-lg">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-sm text-indigo-600 hover:text-indigo-800"
              >
                Mark all as read
              </button>
            )}
          </div>
          <div className="overflow-y-auto flex-1">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                No notifications
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                      !notification.is_read ? 'bg-blue-500' : 'bg-transparent'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className={`font-semibold text-sm ${
                        !notification.is_read ? 'text-gray-900' : 'text-gray-700'
                      }`}>
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatTime(notification.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
