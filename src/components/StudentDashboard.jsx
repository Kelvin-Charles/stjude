import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import ReadingResources from './ReadingResources'

const API_URL = import.meta.env.VITE_API_URL || 'http://102.211.196.167:7700'

export default function StudentDashboard() {
  const { token, user } = useAuth()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [myRank, setMyRank] = useState(null)
  const [myPoints, setMyPoints] = useState(0)
  const [activeTab, setActiveTab] = useState('projects') // 'projects' or 'resources'

  useEffect(() => {
    fetchProjects()
    fetchLeaderboard()
    // Refresh leaderboard every 5 seconds for real-time updates
    const interval = setInterval(fetchLeaderboard, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_URL}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setProjects(data.projects)
      }
    } catch (error) {
      console.error('Error fetching projects:', error)
    } finally {
      setLoading(false)
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
        setMyRank(data.current_user_rank)
        setMyPoints(data.current_user_points || 0)
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    }
  }

  const updateProgress = async (projectId, status, percentage) => {
    try {
      const response = await fetch(`${API_URL}/api/progress`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: projectId,
          status,
          progress_percentage: percentage
        })
      })
      const data = await response.json()
      if (data.success) {
        fetchProjects()
        fetchLeaderboard() // Refresh leaderboard after progress update
        // Don't close modal, let student continue
      }
    } catch (error) {
      console.error('Error updating progress:', error)
    }
  }

  if (loading) {
    return <div className="text-white text-center py-8">Loading projects...</div>
  }

  return (
    <div className="mt-8 flex gap-6">
      {/* Main Content Area */}
      <div className="flex-1">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setActiveTab('projects')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === 'projects'
                  ? 'bg-white text-indigo-600 shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              📁 My Projects
            </button>
            <button
              onClick={() => setActiveTab('resources')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === 'resources'
                  ? 'bg-white text-indigo-600 shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              📚 Reading Resources
            </button>
          </div>
          <div className="bg-white rounded-lg px-4 py-2 shadow-lg">
            <div className="text-sm text-gray-600">Your Points</div>
            <div className="text-2xl font-bold text-indigo-600">{myPoints}</div>
            {myRank && (
              <div className="text-xs text-gray-500">Rank: #{myRank}</div>
            )}
          </div>
        </div>

        {activeTab === 'projects' && (
          <>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div key={project.id} className="bg-white rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-gray-800 mb-2">{project.name}</h3>
            <p className="text-gray-600 mb-4">{project.description}</p>
            
            {project.progress && (
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Progress</span>
                  <span>{project.progress.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{ width: `${project.progress.progress_percentage}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">Status: {project.progress.status}</p>
                {project.progress.mentor_feedback && (
                  <div className="mt-2 p-2 bg-blue-50 rounded text-sm">
                    <strong>Mentor Feedback:</strong> {project.progress.mentor_feedback}
                  </div>
                )}
              </div>
            )}

            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedProject(project)}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
              >
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedProject && (
        <ProjectModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
          onUpdate={updateProgress}
          token={token}
          onLeaderboardUpdate={fetchLeaderboard}
        />
      )}
          </>
        )}

        {activeTab === 'resources' && <ReadingResources />}
      </div>

      {/* Fixed Right Sidebar - Leaderboard */}
      <div className="w-80 flex-shrink-0">
        <div className="bg-white rounded-xl p-4 shadow-lg sticky top-4">
          <h3 className="text-xl font-bold text-gray-800 mb-4">🏆 Leaderboard</h3>
          <div className="max-h-[calc(100vh-200px)] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-100 sticky top-0">
                <tr>
                  <th className="px-2 py-2 text-left text-xs">Rank</th>
                  <th className="px-2 py-2 text-left text-xs">Name</th>
                  <th className="px-2 py-2 text-right text-xs">Points</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry, idx) => (
                  <tr
                    key={entry.student_id}
                    className={`${
                      entry.student_id === user?.id
                        ? 'bg-yellow-100 font-semibold'
                        : idx % 2 === 0
                        ? 'bg-white'
                        : 'bg-gray-50'
                    } border-b`}
                  >
                    <td className="px-2 py-1.5">
                      {entry.rank === 1 && '🥇'}
                      {entry.rank === 2 && '🥈'}
                      {entry.rank === 3 && '🥉'}
                      {entry.rank > 3 && `#${entry.rank}`}
                    </td>
                    <td className="px-2 py-1.5 truncate max-w-[120px]" title={entry.full_name}>
                      {entry.full_name}
                    </td>
                    <td className="px-2 py-1.5 text-right font-bold text-indigo-600">
                      {entry.total_points}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

function ProjectModal({ project, onClose, onUpdate, token, onLeaderboardUpdate }) {
  const [steps, setSteps] = useState([])
  const [stepsLoading, setStepsLoading] = useState(true)
  const [stepsError, setStepsError] = useState('')
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [submitResult, setSubmitResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [projectOutput, setProjectOutput] = useState(null)
  const [loadingOutput, setLoadingOutput] = useState(false)
  const [showOutput, setShowOutput] = useState(false)
  const [showFullCode, setShowFullCode] = useState(false)
  const [showQuiz, setShowQuiz] = useState(false)

  useEffect(() => {
    const fetchSteps = async () => {
      try {
        const res = await fetch(`${API_URL}/api/projects/${project.id}/steps`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        const data = await res.json()
        if (data.success) {
          setSteps(data.steps || [])
          setCurrentStepIndex(0)
        } else {
          setStepsError(data.error || 'Could not load steps for this project.')
        }
      } catch (err) {
        console.error('Error fetching steps', err)
        setStepsError('Network error while loading steps.')
      } finally {
        setStepsLoading(false)
      }
    }

    fetchSteps()
  }, [project.id, token])

  const currentStep = steps[currentStepIndex] || null

  const handleOptionChange = (questionId, opt) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: opt,
    }))
  }

  const handleSubmitStep = async () => {
    if (!currentStep || !currentStep.questions?.length) return
    setSubmitting(true)
    setSubmitResult(null)
    try {
      const res = await fetch(`${API_URL}/api/steps/${currentStep.id}/answer`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answers: answers,
        }),
      })
      const data = await res.json()
      if (data.success) {
        setSubmitResult(data)

        // Update overall project progress from steps
        const totalSteps = steps.length || 1
        const completedSteps = currentStepIndex + (data.all_correct ? 1 : 0)
        const percentage = Math.round((completedSteps / totalSteps) * 100)
        const status = percentage === 100 ? 'completed' : 'in_progress'
        onUpdate(project.id, status, percentage)
        
        // Refresh leaderboard to show updated points
        if (onLeaderboardUpdate) {
          onLeaderboardUpdate()
        }
      } else {
        setSubmitResult({ error: data.error || 'Could not submit answers.' })
      }
    } catch (err) {
      console.error('Error submitting step answers', err)
      setSubmitResult({ error: 'Network error while submitting answers.' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleNextStep = () => {
    setSubmitResult(null)
    setAnswers({})
    setShowQuiz(false)
    setShowFullCode(false)
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1)
    }
  }

  const handleRunProject = async () => {
    setLoadingOutput(true)
    setShowOutput(true)
    try {
      const res = await fetch(`${API_URL}/api/projects/${project.id}/run`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      const data = await res.json()
      if (data.success) {
        setProjectOutput(data.output)
      } else {
        setProjectOutput(`Error: ${data.error || 'Could not run project'}`)
      }
    } catch (err) {
      console.error('Error running project', err)
      setProjectOutput('Network error while running project.')
    } finally {
      setLoadingOutput(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-2xl font-bold mb-2">{project.name}</h3>
            <p className="text-gray-600">{project.description}</p>
          </div>
          <button
            onClick={handleRunProject}
            disabled={loadingOutput}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 font-semibold"
          >
            {loadingOutput ? 'Running...' : '▶️ Run Project & See Output'}
          </button>
        </div>

        {showOutput && projectOutput && (
          <div className="mb-4 p-4 bg-gray-900 rounded-lg">
            <h4 className="text-white font-semibold mb-2">Program Output:</h4>
            <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap overflow-x-auto">
              {projectOutput}
            </pre>
          </div>
        )}

        {stepsLoading && <div>Loading steps...</div>}
        {stepsError && <div className="text-red-600 mb-4">{stepsError}</div>}

        {!stepsLoading && !stepsError && steps.length === 0 && (
          <div className="text-gray-700">
            No steps released yet. Please wait for your mentor/manager to release the project steps.
          </div>
        )}

        {currentStep && (
          <div className="mt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-500">
                Step {currentStep.order_index} of {steps.length}
              </span>
            </div>

            <h4 className="text-xl font-semibold mb-2">{currentStep.title}</h4>
            <p className="whitespace-pre-line text-gray-800 mb-4">{currentStep.content}</p>

            {/* Multiple Code Snippets - Hidden when quiz is shown */}
            {!showQuiz && currentStep.code_snippet && (() => {
              try {
                const codeSnippets = JSON.parse(currentStep.code_snippet);
                if (Array.isArray(codeSnippets) && codeSnippets.length > 0) {
                  return (
                    <div className="mb-4 space-y-4">
                      {codeSnippets.map((snippet, idx) => (
                        <div key={idx}>
                          <h5 className="font-semibold mb-2 text-indigo-600">
                            {snippet.title || `Code Example ${idx + 1}`}
                          </h5>
                          {snippet.explanation && (
                            <p className="text-sm text-gray-600 mb-2">{snippet.explanation}</p>
                          )}
                          <pre className="bg-gray-900 text-gray-100 text-sm p-4 rounded-lg overflow-x-auto border-2 border-gray-700">
                            <code>{snippet.code}</code>
                          </pre>
                        </div>
                      ))}
                      
                      {/* Full Code Preview Button */}
                      {currentStep.full_code && (
                        <div className="mt-4">
                          <button
                            onClick={() => setShowFullCode(!showFullCode)}
                            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm font-semibold"
                          >
                            {showFullCode ? '🔽 Hide Full Code' : '👁️ Preview Full Code'}
                          </button>
                          {showFullCode && (
                            <div className="mt-3">
                              <h5 className="font-semibold mb-2 text-purple-600">Complete Program Code:</h5>
                              <pre className="bg-gray-900 text-gray-100 text-sm p-4 rounded-lg overflow-x-auto border-2 border-purple-500">
                                <code>{currentStep.full_code}</code>
                              </pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                }
              } catch (e) {
                // Fallback to old format if not JSON
                return (
                  <div className="mb-4">
                    <h5 className="font-semibold mb-2">Code Example:</h5>
                    <pre className="bg-gray-900 text-gray-100 text-sm p-4 rounded-lg overflow-x-auto border-2 border-gray-700">
                      <code>{currentStep.code_snippet}</code>
                    </pre>
                  </div>
                );
              }
            })()}

            {currentStep.questions && currentStep.questions.length > 0 && (
              <div className="mt-4 space-y-4">
                <div className="flex justify-between items-center">
                  <h5 className="font-semibold text-lg">
                    Questions for this step ({currentStep.questions.length} questions)
                  </h5>
                  <button
                    onClick={() => {
                      setShowQuiz(!showQuiz);
                      setShowFullCode(false);
                    }}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-semibold"
                  >
                    {showQuiz ? '👁️ Show Codes Again' : '📝 Start Quiz (Hide Codes)'}
                  </button>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Answer all questions carefully. If you get a question wrong and retry, you'll only earn 50% of the points.
                </p>

                {/* Only show question cards when quiz is active (codes are hidden) */}
                {showQuiz &&
                  currentStep.questions.map((q) => (
                    <div key={q.id} className="border rounded-lg p-3">
                      <p className="font-medium mb-2">{q.prompt}</p>
                      <div className="space-y-1 text-sm">
                        {Object.entries(q.options || {}).map(([optKey, optVal]) =>
                          optVal ? (
                            <label key={optKey} className="flex items-center space-x-2">
                              <input
                                type="radio"
                                name={`q-${q.id}`}
                                value={optKey}
                                checked={answers[q.id] === optKey}
                                onChange={() => handleOptionChange(q.id, optKey)}
                              />
                              <span>
                                <strong>{optKey}:</strong> {optVal}
                              </span>
                            </label>
                          ) : null
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            )}

            {submitResult?.error && (
              <div className="mt-3 p-2 rounded bg-red-100 text-red-700 text-sm">
                {submitResult.error}
              </div>
            )}

            {submitResult && !submitResult.error && (
              <div className={`mt-3 p-4 rounded-lg ${
                submitResult.all_correct 
                  ? 'bg-green-50 border-2 border-green-500' 
                  : 'bg-yellow-50 border-2 border-yellow-500'
              }`}>
                <p className="font-bold text-lg mb-2">
                  {submitResult.all_correct ? '✅ Perfect!' : '⚠️ Some answers need review'}
                </p>
                <p className="font-semibold mb-1">
                  You scored <span className="text-indigo-600">{submitResult.total_points}</span> / {submitResult.max_points} points for this step.
                </p>
                {submitResult.all_correct ? (
                  <p className="text-green-700">🎉 Excellent work! All answers are correct. You earned {submitResult.total_points} points!</p>
                ) : (
                  <div>
                    <p className="text-yellow-700 mb-2">Some answers were incorrect. Review the explanations above and try again.</p>
                    <div className="mt-2 space-y-1">
                      {submitResult.results?.map((result, idx) => (
                        <div key={idx} className={`text-sm ${result.is_correct ? 'text-green-700' : 'text-red-700'}`}>
                          {result.is_correct ? '✓' : '✗'} Question {idx + 1}: {result.is_correct ? 'Correct' : 'Incorrect'} ({result.points_awarded}/{result.max_points} pts)
                          {result.is_retry && result.was_previously_correct === false && (
                            <span className="ml-2 text-orange-600 font-semibold">
                              ⚠️ Retry: Points reduced by 50%
                            </span>
                          )}
                          {result.is_retry && result.was_previously_correct === true && (
                            <span className="ml-2 text-gray-600">
                              (Already answered correctly - no additional points)
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 p-2 bg-orange-100 border border-orange-300 rounded text-sm text-orange-800">
                      <strong>⚠️ Retry Penalty:</strong> If you got a question wrong and try again, you'll only earn 50% of the original points for that question.
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="flex space-x-2 mt-6">
              <button
                onClick={handleSubmitStep}
                disabled={submitting || !currentStep.questions?.length}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit answers for this step'}
              </button>

              <button
                onClick={onClose}
                className="flex-1 bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400"
              >
                Close
              </button>
            </div>

            {/* Allow moving to next step after at least one submission on this step */}
            {submitResult && submitResult.results?.length > 0 && currentStepIndex < steps.length - 1 && (
              <button
                onClick={handleNextStep}
                className="mt-3 w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-bold text-lg shadow-lg"
              >
                ➡️ Continue to Next Step
              </button>
            )}
            
            {submitResult?.all_correct && currentStepIndex === steps.length - 1 && (
              <div className="mt-3 p-4 bg-green-100 border-2 border-green-500 rounded-lg">
                <p className="font-bold text-lg text-green-800 mb-2">🎊 Congratulations!</p>
                <p className="text-green-700">You've completed all steps in this project! Great job!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
