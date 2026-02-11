import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { toast } from 'react-toastify'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function MentorDashboard() {
  const { token } = useAuth()
  const [students, setStudents] = useState([])
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [leaderboard, setLeaderboard] = useState([])
  const [showLeaderboard, setShowLeaderboard] = useState(true)
  const [activeTab, setActiveTab] = useState('overview') // 'overview', 'resources', or 'submissions'
  const [resources, setResources] = useState([])
  const [showCreateResource, setShowCreateResource] = useState(false)
  const [newResource, setNewResource] = useState({
    title: '',
    content: '',
    description: '',
    category: 'General'
  })
  const [submissions, setSubmissions] = useState([])
  const [selectedSubmission, setSelectedSubmission] = useState(null)
  const [submissionContent, setSubmissionContent] = useState(null)
  const [loadingSubmissions, setLoadingSubmissions] = useState(false)
  const [reviewNotes, setReviewNotes] = useState('')
  const [reviewStatus, setReviewStatus] = useState('submitted')

  useEffect(() => {
    fetchStudents()
    fetchReport()
    fetchLeaderboard()
    fetchResources()
    // Refresh leaderboard every 5 seconds for real-time updates
    const interval = setInterval(fetchLeaderboard, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (activeTab === 'submissions') {
      fetchSubmissions()
    }
  }, [activeTab])

  const fetchStudents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/students`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setStudents(data.students)
      }
    } catch (error) {
      console.error('Error fetching students:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchReport = async () => {
    try {
      const response = await fetch(`${API_URL}/api/reports/overview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setReport(data.report)
      }
    } catch (error) {
      console.error('Error fetching report:', error)
    }
  }

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${API_URL}/api/leaderboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setLeaderboard(data.leaderboard || [])
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    }
  }

  const fetchResources = async () => {
    try {
      const response = await fetch(`${API_URL}/api/resources`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setResources(data.resources || [])
      }
    } catch (error) {
      console.error('Error fetching resources:', error)
    }
  }

  const handleCreateResource = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_URL}/api/resources`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newResource)
      })
      const data = await response.json()
      if (data.success) {
        setShowCreateResource(false)
        setNewResource({ title: '', content: '', description: '', category: 'General' })
        fetchResources()
      }
    } catch (error) {
      console.error('Error creating resource:', error)
    }
  }

  const fetchSubmissions = async () => {
    setLoadingSubmissions(true)
    try {
      const response = await fetch(`${API_URL}/api/admin/submissions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setSubmissions(data.submissions || [])
      }
    } catch (error) {
      console.error('Error fetching submissions:', error)
    } finally {
      setLoadingSubmissions(false)
    }
  }

  const fetchSubmissionContent = async (submissionId) => {
    try {
      const response = await fetch(`${API_URL}/api/submissions/${submissionId}/content`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setSubmissionContent(data)
      } else {
        toast.error('Error loading file: ' + data.error, {
          position: "top-right",
          autoClose: 3000,
        })
      }
    } catch (error) {
      console.error('Error fetching submission content:', error)
      toast.error('Error loading file content', {
        position: "top-right",
        autoClose: 3000,
      })
    }
  }

  const handleViewSubmission = async (submission) => {
    setSelectedSubmission(submission)
    setReviewNotes(submission.review_notes || '')
    setReviewStatus(submission.status || 'submitted')
    setSubmissionContent(null)
    await fetchSubmissionContent(submission.id)
  }

  const handleReviewSubmission = async () => {
    if (!selectedSubmission) return
    
    try {
      const response = await fetch(`${API_URL}/api/submissions/${selectedSubmission.id}/review`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          review_notes: reviewNotes,
          status: reviewStatus
        })
      })
      const data = await response.json()
      if (data.success) {
        toast.success('Review submitted successfully!', {
          position: "top-right",
          autoClose: 3000,
        })
        setSelectedSubmission(null)
        fetchSubmissions()
      } else {
        toast.error('Error submitting review: ' + data.error, {
          position: "top-right",
          autoClose: 3000,
        })
      }
    } catch (error) {
      console.error('Error reviewing submission:', error)
      toast.error('Error submitting review', {
        position: "top-right",
        autoClose: 3000,
      })
    }
  }

  const fetchStudentProgress = async (studentId) => {
    try {
      const response = await fetch(`${API_URL}/api/students/${studentId}/progress`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setSelectedStudent(data)
      }
    } catch (error) {
      console.error('Error fetching student progress:', error)
    }
  }

  if (loading) {
    return <div className="text-white text-center py-8">Loading...</div>
  }

  return (
    <div className="mt-8">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          <h2 className="text-3xl font-bold text-white">Mentor Dashboard</h2>
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg font-semibold ${
              activeTab === 'overview'
                ? 'bg-white text-indigo-600'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('resources')}
            className={`px-4 py-2 rounded-lg font-semibold ${
              activeTab === 'resources'
                ? 'bg-white text-indigo-600'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Manage Resources
          </button>
          <button
            onClick={() => setActiveTab('submissions')}
            className={`px-4 py-2 rounded-lg font-semibold ${
              activeTab === 'submissions'
                ? 'bg-white text-indigo-600'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            📤 Submissions
          </button>
        </div>
        <button
          onClick={() => setShowLeaderboard(!showLeaderboard)}
          className="bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600 font-semibold shadow-lg"
        >
          {showLeaderboard ? 'Hide' : 'Show'} Leaderboard
        </button>
      </div>

      {showLeaderboard && (
        <div className="bg-white rounded-xl p-6 shadow-lg mb-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">🏆 Student Leaderboard (Real-time)</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left">Rank</th>
                  <th className="px-4 py-2 text-left">Student Name</th>
                  <th className="px-4 py-2 text-left">Username</th>
                  <th className="px-4 py-2 text-right">Total Points</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry, idx) => (
                  <tr
                    key={entry.student_id}
                    className={`${
                      idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                    } border-b`}
                  >
                    <td className="px-4 py-2">
                      {entry.rank === 1 && '🥇'}
                      {entry.rank === 2 && '🥈'}
                      {entry.rank === 3 && '🥉'}
                      {entry.rank > 3 && `#${entry.rank}`}
                    </td>
                    <td className="px-4 py-2">{entry.full_name}</td>
                    <td className="px-4 py-2 text-gray-600">{entry.username}</td>
                    <td className="px-4 py-2 text-right font-bold text-indigo-600">
                      {entry.total_points} pts
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'overview' && (
        <>
          {report && (
            <div className="bg-white rounded-xl p-6 shadow-lg mb-6">
              <h3 className="text-xl font-bold mb-4">Overview Report</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Total Students</p>
                  <p className="text-2xl font-bold">{report.total_students}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Total Projects</p>
                  <p className="text-2xl font-bold">{report.total_projects}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold">{report.progress_stats.in_progress}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold">{report.progress_stats.completed}</p>
                </div>
              </div>
            </div>
          )}

          <div className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold mb-4">Students</h3>
            <div className="space-y-2">
              {students.map((student) => (
                <div
                  key={student.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => fetchStudentProgress(student.id)}
                >
                  <div>
                    <p className="font-semibold">{student.full_name}</p>
                    <p className="text-sm text-gray-600">{student.email}</p>
                  </div>
                  <button className="text-indigo-600 hover:underline">View Progress</button>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {selectedStudent && (
        <StudentProgressModal
          studentData={selectedStudent}
          onClose={() => setSelectedStudent(null)}
          token={token}
        />
      )}

      {activeTab === 'resources' && (
        <div className="bg-white rounded-xl p-6 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-2xl font-bold text-gray-800">📚 Manage Reading Resources</h3>
            <button
              onClick={() => setShowCreateResource(!showCreateResource)}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 font-semibold"
            >
              {showCreateResource ? 'Cancel' : '+ Create Resource'}
            </button>
          </div>

          {showCreateResource && (
            <form onSubmit={handleCreateResource} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="space-y-4">
                <div>
                  <label className="block mb-2 font-medium">Title</label>
                  <input
                    type="text"
                    value={newResource.title}
                    onChange={(e) => setNewResource({ ...newResource, title: e.target.value })}
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Resource title"
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">Description (optional)</label>
                  <input
                    type="text"
                    value={newResource.description}
                    onChange={(e) => setNewResource({ ...newResource, description: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Short description"
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">Category</label>
                  <input
                    type="text"
                    value={newResource.category}
                    onChange={(e) => setNewResource({ ...newResource, category: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="e.g., Python Basics, Loops, etc."
                  />
                </div>
                <div>
                  <label className="block mb-2 font-medium">Content</label>
                  <textarea
                    value={newResource.content}
                    onChange={(e) => setNewResource({ ...newResource, content: e.target.value })}
                    required
                    rows="10"
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Write the resource content here..."
                  />
                </div>
                <button
                  type="submit"
                  className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Create Resource
                </button>
              </div>
            </form>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {resources.map((resource) => (
              <div key={resource.id} className="border rounded-lg p-4">
                <h4 className="font-bold text-lg mb-2">{resource.title}</h4>
                {resource.category && (
                  <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded mb-2 inline-block">
                    {resource.category}
                  </span>
                )}
                <p className="text-sm text-gray-600 mb-2">{resource.description}</p>
                <p className="text-xs text-gray-500">
                  Created: {new Date(resource.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'submissions' && (
        <div className="bg-white rounded-xl p-6 shadow-lg">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">📤 Student Submissions</h3>
          
          {loadingSubmissions ? (
            <div className="text-center py-8">Loading submissions...</div>
          ) : submissions.length === 0 ? (
            <div className="text-center py-8 text-gray-600">No submissions yet.</div>
          ) : (
            <div className="space-y-4">
              {submissions.map((submission) => (
                <div key={submission.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-bold text-lg">{submission.filename}</h4>
                        <span className={`px-2 py-1 rounded text-xs ${
                          submission.status === 'approved' ? 'bg-green-100 text-green-800' :
                          submission.status === 'needs_revision' ? 'bg-red-100 text-red-800' :
                          submission.status === 'reviewed' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {submission.status}
                        </span>
                        {submission.submission_type === 'final_project' && (
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                            Final Project
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">
                        <strong>Student:</strong> {submission.student_name}
                        {submission.project_name && (
                          <> • <strong>Project:</strong> {submission.project_name}</>
                        )}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Submitted: {new Date(submission.submitted_at).toLocaleString()}
                        {submission.reviewed_at && (
                          <> • Reviewed: {new Date(submission.reviewed_at).toLocaleString()}</>
                        )}
                      </p>
                      {submission.notes && (
                        <p className="text-sm text-gray-700 mt-2 italic">Notes: {submission.notes}</p>
                      )}
                      {submission.review_notes && (
                        <div className="mt-2 p-2 bg-blue-50 rounded">
                          <p className="text-sm font-semibold">Review Notes:</p>
                          <p className="text-sm text-gray-700">{submission.review_notes}</p>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => handleViewSubmission(submission)}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm"
                      >
                        👁️ View Code
                      </button>
                      <a
                        href={`${API_URL}/api/submissions/${submission.id}/download`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          // Add auth header via fetch instead
                          e.preventDefault()
                          fetch(`${API_URL}/api/submissions/${submission.id}/download`, {
                            headers: {
                              'Authorization': `Bearer ${token}`
                            }
                          }).then(res => res.blob()).then(blob => {
                            const url = window.URL.createObjectURL(blob)
                            const a = document.createElement('a')
                            a.href = url
                            a.download = submission.filename
                            a.click()
                            window.URL.revokeObjectURL(url)
                          })
                        }}
                      >
                        📥 Download
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Submission View Modal */}
      {selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 max-w-5xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-2xl font-bold mb-2">{selectedSubmission.filename}</h3>
                <p className="text-gray-600">
                  Student: <strong>{selectedSubmission.student_name}</strong>
                  {selectedSubmission.project_name && (
                    <> • Project: <strong>{selectedSubmission.project_name}</strong></>
                  )}
                </p>
                <p className="text-sm text-gray-500">
                  Submitted: {new Date(selectedSubmission.submitted_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedSubmission(null)
                  setSubmissionContent(null)
                }}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            {/* Code Viewer */}
            {submissionContent && (
              <div className="mb-4">
                <h4 className="font-bold mb-2">Source Code:</h4>
                {submissionContent.is_binary ? (
                  <div className="bg-gray-100 p-4 rounded">
                    <p className="text-gray-600">This is a binary file. Please download to view.</p>
                  </div>
                ) : (
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{submissionContent.content}</code>
                  </pre>
                )}
              </div>
            )}

            {/* Review Section */}
            <div className="border-t pt-4">
              <h4 className="font-bold mb-2">Review Submission</h4>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Status:</label>
                <select
                  value={reviewStatus}
                  onChange={(e) => setReviewStatus(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="submitted">Submitted</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="approved">Approved</option>
                  <option value="needs_revision">Needs Revision</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Review Notes:</label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Add your review notes and feedback..."
                  className="w-full px-3 py-2 border rounded-lg h-32"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleReviewSubmission}
                  className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
                >
                  Submit Review
                </button>
                <button
                  onClick={() => {
                    setSelectedSubmission(null)
                    setSubmissionContent(null)
                  }}
                  className="bg-gray-300 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function StudentProgressModal({ studentData, onClose, token }) {
  const [feedback, setFeedback] = useState({})

  const handleAddFeedback = async (progressId, feedbackText) => {
    try {
      const response = await fetch(`${API_URL}/api/progress/${progressId}/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ feedback: feedbackText })
      })
      const data = await response.json()
      if (data.success) {
        // Refresh student data
        window.location.reload()
      }
    } catch (error) {
      console.error('Error adding feedback:', error)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <h3 className="text-2xl font-bold mb-4">
          Progress for {studentData.student.full_name}
        </h3>

        <div className="space-y-4">
          {studentData.progress.map((prog) => (
            <div key={prog.id} className="border rounded-lg p-4">
              <div className="flex justify-between mb-2">
                <h4 className="font-semibold">{prog.project_name}</h4>
                <span className={`px-2 py-1 rounded text-sm ${
                  prog.status === 'completed' ? 'bg-green-100 text-green-800' :
                  prog.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {prog.status}
                </span>
              </div>
              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <span>Progress</span>
                  <span>{prog.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{ width: `${prog.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
              {prog.notes && (
                <p className="text-sm text-gray-600 mb-2">Notes: {prog.notes}</p>
              )}
              {prog.mentor_feedback && (
                <div className="bg-blue-50 p-2 rounded text-sm mb-2">
                  <strong>Your Feedback:</strong> {prog.mentor_feedback}
                </div>
              )}
              <div className="mt-2">
                <textarea
                  placeholder="Add feedback..."
                  value={feedback[prog.id] || ''}
                  onChange={(e) => setFeedback({ ...feedback, [prog.id]: e.target.value })}
                  className="w-full px-3 py-2 border rounded text-sm"
                  rows="2"
                />
                <button
                  onClick={() => {
                    if (feedback[prog.id]) {
                      handleAddFeedback(prog.id, feedback[prog.id])
                      setFeedback({ ...feedback, [prog.id]: '' })
                    }
                  }}
                  className="mt-1 bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                >
                  Add Feedback
                </button>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={onClose}
          className="mt-6 w-full bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400"
        >
          Close
        </button>
      </div>
    </div>
  )
}
