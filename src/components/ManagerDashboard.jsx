import MentorDashboard from './MentorDashboard'
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function ManagerDashboard() {
  const { token } = useAuth()
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    project_path: '',
    difficulty_level: 'beginner',
    estimated_time: ''
  })
  const [showCreateForm, setShowCreateForm] = useState(false)

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
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-semibold"
        >
          {showCreateForm ? 'Cancel' : '+ Create Project'}
        </button>
      </div>

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
