import MentorDashboard from './MentorDashboard'
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function ManagerDashboard() {
  const { token } = useAuth()
  const [students, setStudents] = useState([])
  const [studentsLoading, setStudentsLoading] = useState(false)
  const [studentsError, setStudentsError] = useState('')
  const [showReset, setShowReset] = useState(false)
  const [resetForm, setResetForm] = useState({ studentId: '', password: '', generate: true })
  const [resetMsg, setResetMsg] = useState('')
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    project_path: '',
    difficulty_level: 'beginner',
    estimated_time: ''
  })
  const [showCreateForm, setShowCreateForm] = useState(false)

  const fetchStudents = async () => {
    if (!token) return
    setStudentsLoading(true)
    setStudentsError('')
    try {
      const res = await fetch(`${API_URL}/api/students`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok || !data.success) {
        setStudents([])
        setStudentsError(data.error || `Could not load students (HTTP ${res.status}).`)
        return
      }
      setStudents(data.students || [])
      if ((data.students || []).length === 0) {
        setStudentsError('No students found yet. Register a student first.')
      }
    } catch (e) {
      setStudents([])
      setStudentsError('Network error while loading students.')
    } finally {
      setStudentsLoading(false)
    }
  }

  useEffect(() => {
    if (showReset) fetchStudents()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showReset, token])

  const handleResetPassword = async (e) => {
    e.preventDefault()
    setResetMsg('')
    if (!resetForm.studentId) {
      setResetMsg('Pick a student first.')
      return
    }
    try {
      const res = await fetch(
        `${API_URL}/api/admin/students/${resetForm.studentId}/reset-password`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            generate: resetForm.generate,
            password: resetForm.generate ? undefined : resetForm.password,
          }),
        }
      )
      const data = await res.json()
      if (!data.success) {
        setResetMsg(data.error || 'Could not reset password.')
        return
      }
      if (data.temporary_password) {
        setResetMsg(`Temporary password: ${data.temporary_password}`)
      } else {
        setResetMsg('Password updated.')
      }
      setResetForm((p) => ({ ...p, password: '' }))
    } catch (err) {
      setResetMsg('Network error while resetting password.')
    }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_URL}/api/admin/projects`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newProject)
      })
      const data = await response.json()
      if (data.success) {
        setShowCreateForm(false)
        setNewProject({
          name: '',
          description: '',
          project_path: '',
          difficulty_level: 'beginner',
          estimated_time: ''
        })
        window.location.reload()
      }
    } catch (error) {
      console.error('Error creating project:', error)
    }
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-3xl font-bold text-white">Manager Dashboard</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setShowReset(!showReset)}
            className="bg-yellow-500 text-white px-6 py-3 rounded-lg hover:bg-yellow-600 font-semibold"
          >
            {showReset ? 'Close' : 'Reset Student Password'}
          </button>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-semibold"
          >
            {showCreateForm ? 'Cancel' : '+ Create Project'}
          </button>
        </div>
      </div>

      {showReset && (
        <div className="bg-white rounded-xl p-6 shadow-lg mb-6">
          <h3 className="text-xl font-bold mb-4">Reset Student Password</h3>
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div>
              <label className="block mb-2 font-medium">Student</label>
              <select
                value={resetForm.studentId}
                onChange={(e) => setResetForm((p) => ({ ...p, studentId: e.target.value }))}
                className="w-full px-4 py-2 border rounded-lg"
                required
              >
                <option value="">Select a student...</option>
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.full_name} ({s.username})
                  </option>
                ))}
              </select>
              <div className="mt-2 flex items-center gap-3 text-sm">
                {studentsLoading && <span className="text-gray-600">Loading students…</span>}
                {studentsError && <span className="text-red-600">{studentsError}</span>}
                <button
                  type="button"
                  onClick={fetchStudents}
                  className="ml-auto text-indigo-600 hover:underline"
                >
                  Refresh
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                id="generatePw"
                type="checkbox"
                checked={resetForm.generate}
                onChange={(e) =>
                  setResetForm((p) => ({ ...p, generate: e.target.checked }))
                }
              />
              <label htmlFor="generatePw" className="text-sm text-gray-700">
                Generate temporary password automatically
              </label>
            </div>

            {!resetForm.generate && (
              <div>
                <label className="block mb-2 font-medium">New Password</label>
                <input
                  type="text"
                  value={resetForm.password}
                  onChange={(e) => setResetForm((p) => ({ ...p, password: e.target.value }))}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder="Enter new password"
                  required
                />
              </div>
            )}

            {resetMsg && (
              <div className="p-3 rounded-lg bg-indigo-50 text-indigo-700 text-sm">
                {resetMsg}
              </div>
            )}

            <button
              type="submit"
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
            >
              Reset Password
            </button>
          </form>
        </div>
      )}

      {showCreateForm && (
        <div className="bg-white rounded-xl p-6 shadow-lg mb-6">
          <h3 className="text-xl font-bold mb-4">Create New Project</h3>
          <form onSubmit={handleCreateProject} className="space-y-4">
            <div>
              <label className="block mb-2 font-medium">Project Name</label>
              <input
                type="text"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                required
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block mb-2 font-medium">Description</label>
              <textarea
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg"
                rows="3"
              />
            </div>
            <div>
              <label className="block mb-2 font-medium">Project Path (folder name)</label>
              <input
                type="text"
                value={newProject.project_path}
                onChange={(e) => setNewProject({ ...newProject, project_path: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block mb-2 font-medium">Difficulty Level</label>
                <select
                  value={newProject.difficulty_level}
                  onChange={(e) => setNewProject({ ...newProject, difficulty_level: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
              <div>
                <label className="block mb-2 font-medium">Estimated Time (minutes)</label>
                <input
                  type="number"
                  value={newProject.estimated_time}
                  onChange={(e) => setNewProject({ ...newProject, estimated_time: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>
            </div>
            <button
              type="submit"
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
            >
              Create Project
            </button>
          </form>
        </div>
      )}

      <MentorDashboard />
    </div>
  )
}
