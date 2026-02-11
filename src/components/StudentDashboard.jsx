import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import ReadingResources from './ReadingResources'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function StudentDashboard() {
  const { token, user } = useAuth()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState(null)
  const [selectedProjectForSubmission, setSelectedProjectForSubmission] = useState(null)
  const [showFinalProjectSubmission, setShowFinalProjectSubmission] = useState(false)
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
        // Refresh projects list to show updated progress
        await fetchProjects()
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
            {/* Final Project Submission Section */}
            <div className="bg-white rounded-xl p-6 shadow-lg mb-6 border-2 border-purple-300">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">🎯 Final Project Submission</h3>
                  <p className="text-gray-600">Submit your final project work for evaluation (not tied to any specific project)</p>
                </div>
                <button
                  onClick={() => setShowFinalProjectSubmission(true)}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 font-semibold text-lg"
                >
                  Submit Final Project
                </button>
              </div>
            </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        {projects.map((project) => {
          const isBasic = project.description?.toLowerCase().includes('challenge');
          
          return (
            <div 
              key={project.id} 
              className={`group bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border-t-4 ${
                isBasic ? 'border-teal-500' : 'border-indigo-600'
              } flex flex-col h-full`}
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-xl font-bold text-gray-800 leading-tight group-hover:text-indigo-600 transition-colors">
                  {project.name}
                </h3>
                {isBasic && (
                  <span className="bg-teal-100 text-teal-700 text-[10px] uppercase font-black px-2 py-1 rounded-md tracking-wider">
                    Basic
                  </span>
                )}
              </div>
              
              <p className="text-gray-500 text-sm mb-6 flex-grow leading-relaxed">
                {project.description}
              </p>
            
              <div className="mb-6 bg-gray-50 p-3 rounded-xl border border-gray-100">
                <div className="flex justify-between text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">
                  <span>Progress</span>
                  <span className="text-indigo-600">
                    {project.progress ? project.progress.progress_percentage : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                    style={{ width: `${project.progress ? project.progress.progress_percentage : 0}%` }}
                  ></div>
                </div>
                <div className="mt-2 flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    project.progress?.status === 'completed' ? 'bg-green-500' : 
                    project.progress?.status === 'in_progress' ? 'bg-amber-500' : 'bg-gray-300'
                  }`}></div>
                  <p className="text-[11px] font-bold text-gray-400 uppercase tracking-tight">
                    {project.progress ? project.progress.status.replace('_', ' ') : 'not started'}
                  </p>
                  </div>
              </div>

              <div className="flex gap-3 mt-auto">
              <button
                onClick={() => setSelectedProject(project)}
                  className="flex-1 bg-gray-100 text-gray-700 px-4 py-2.5 rounded-xl hover:bg-indigo-600 hover:text-white transition-all duration-200 font-bold text-sm whitespace-nowrap"
              >
                View Details
              </button>
                <button
                  onClick={() => setSelectedProjectForSubmission({...project, submissionType: 'project'})}
                  className="flex-1 bg-green-600 text-white px-4 py-2.5 rounded-xl hover:bg-green-700 hover:scale-[1.02] active:scale-95 transition-all duration-200 font-bold text-sm whitespace-nowrap flex items-center justify-center gap-2 shadow-sm shadow-green-200"
                >
                  <span>📤</span> Submit
                </button>
            </div>
          </div>
          );
        })}
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

      {selectedProjectForSubmission && (
        <SubmissionModal
          project={selectedProjectForSubmission}
          onClose={() => setSelectedProjectForSubmission(null)}
          token={token}
          onSuccess={() => {
            setSelectedProjectForSubmission(null)
            fetchProjects()
          }}
        />
      )}

      {showFinalProjectSubmission && (
        <FinalProjectSubmissionModal
          onClose={() => setShowFinalProjectSubmission(false)}
          token={token}
          onSuccess={() => {
            setShowFinalProjectSubmission(false)
          }}
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
  const [stepProgress, setStepProgress] = useState([])
  const [projectProgress, setProjectProgress] = useState(null)

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
    fetchProjectProgress()
  }, [project.id, token])

  // Set current step to first incomplete step when steps and progress are loaded
  useEffect(() => {
    if (steps.length > 0 && stepProgress.length > 0) {
      // Find the first incomplete step
      let firstIncompleteIndex = -1
      for (let i = 0; i < steps.length; i++) {
        const stepProg = stepProgress.find(sp => sp.step_id === steps[i].id)
        if (!stepProg || !stepProg.is_completed) {
          firstIncompleteIndex = i
          break
        }
      }
      
      // If all steps are completed, show the last step
      // Otherwise, show the first incomplete step
      if (firstIncompleteIndex === -1) {
        setCurrentStepIndex(steps.length - 1)
      } else {
        setCurrentStepIndex(firstIncompleteIndex)
      }
    }
  }, [steps, stepProgress])

  const fetchProjectProgress = async () => {
    try {
      const res = await fetch(`${API_URL}/api/projects/${project.id}/progress`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      const data = await res.json()
      if (data.success) {
        setProjectProgress(data.progress)
        setStepProgress(data.step_progress || [])
      }
    } catch (err) {
      console.error('Error fetching project progress:', err)
    }
  }

  const currentStep = steps[currentStepIndex] || null
  const currentStepProgress = currentStep ? stepProgress.find(sp => sp.step_id === currentStep.id) : null
  const isCurrentStepCompleted = currentStepProgress?.is_completed || false

  // Load previous answers when viewing a completed step
  useEffect(() => {
    if (currentStep && currentStep.questions && isCurrentStepCompleted) {
      // Fetch previous answers for this step
      const loadPreviousAnswers = async () => {
        try {
          const res = await fetch(`${API_URL}/api/steps/${currentStep.id}/answers`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
          const data = await res.json()
          if (data.success && data.has_answers) {
            // Set previous answers
            setAnswers(data.answers)
            // Set submit result to show previous submission
            setSubmitResult({
              results: data.results,
              total_points: data.total_points,
              max_points: data.max_points,
              all_correct: data.all_correct,
            })
          }
        } catch (err) {
          console.error('Error loading previous answers:', err)
        }
      }
      loadPreviousAnswers()
    } else {
      // Clear answers when viewing a new incomplete step
      setAnswers({})
      setSubmitResult(null)
    }
  }, [currentStep?.id, isCurrentStepCompleted, project.id, token])

  const handleOptionChange = (questionId, opt) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: opt,
    }))
  }

  const handlePreviousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1)
      setSubmitResult(null)
      setAnswers({})
      setShowQuiz(false)
      setShowFullCode(false)
    }
  }

  const handleNextStep = async () => {
    setSubmitResult(null)
    setAnswers({})
    setShowQuiz(false)
    setShowFullCode(false)
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1)
      // Refresh progress after moving to next step
      await fetchProjectProgress()
    }
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

        // Refresh project progress to get accurate calculation from backend
        await fetchProjectProgress()
        
        // Update overall project progress (backend will calculate accurately)
        if (projectProgress) {
          onUpdate(project.id, projectProgress.status, projectProgress.progress_percentage)
        } else {
          // Fallback calculation
          const totalSteps = steps.length || 1
          const completedSteps = currentStepIndex + 1
          const percentage = Math.round((completedSteps / totalSteps) * 100)
          const status = percentage === 100 ? 'completed' : 'in_progress'
          onUpdate(project.id, status, percentage)
        }
        
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
              {projectProgress && (
                <div className="text-sm">
                  <span className="text-gray-600">Project Progress: </span>
                  <span className="font-bold text-indigo-600">{projectProgress.progress_percentage}%</span>
                  {stepProgress.find(sp => sp.step_id === currentStep.id)?.is_completed && (
                    <span className="ml-2 text-green-600">✓ Completed</span>
                  )}
                </div>
              )}
            </div>

            <h4 className="text-xl font-semibold mb-2">{currentStep.title}</h4>
            <p className="whitespace-pre-line text-gray-800 mb-4">{currentStep.content}</p>

            {/* Step Progress Indicator */}
            {steps.length > 1 && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Steps Completed:</span>
                  <span className="text-sm font-bold text-indigo-600">
                    {stepProgress.filter(sp => sp.is_completed).length} / {steps.length}
                  </span>
                </div>
                <div className="flex gap-2">
                  {steps.map((step, idx) => {
                    const stepProg = stepProgress.find(sp => sp.step_id === step.id)
                    const isCompleted = stepProg?.is_completed || false
                    const isCurrent = idx === currentStepIndex
                    return (
                      <button
                        key={step.id}
                        onClick={() => {
                          setCurrentStepIndex(idx)
                          setSubmitResult(null)
                          setAnswers({})
                          setShowQuiz(false)
                          setShowFullCode(false)
                        }}
                        className={`flex-1 h-2 rounded transition-all hover:scale-105 ${
                          isCompleted
                            ? 'bg-green-500 hover:bg-green-600'
                            : isCurrent
                            ? 'bg-indigo-500 hover:bg-indigo-600'
                            : 'bg-gray-300 hover:bg-gray-400'
                        }`}
                        title={`Step ${step.order_index}: ${isCompleted ? 'Completed' : isCurrent ? 'Current' : 'Not started'} - Click to view`}
                      />
                    )
                  })}
                </div>
              </div>
            )}

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

            {/* Show completion message if step is already completed */}
            {isCurrentStepCompleted && !submitResult && (
              <div className="mt-4 p-4 bg-green-50 border-2 border-green-500 rounded-lg">
                <p className="font-bold text-lg text-green-800 mb-2">✓ Step Completed</p>
                <p className="text-green-700">
                  You've already completed this step. You earned {currentStepProgress?.points_earned || 0} / {currentStepProgress?.points_possible || 0} points.
                </p>
              </div>
            )}

            <div className="flex space-x-2 mt-6">
              <button
                onClick={handleSubmitStep}
                disabled={submitting || !currentStep.questions?.length || isCurrentStepCompleted}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : isCurrentStepCompleted ? 'Already Completed' : 'Submit answers for this step'}
              </button>

              <button
                onClick={onClose}
                className="flex-1 bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400"
              >
                Close
              </button>
            </div>

            {/* Navigation buttons */}
            <div className="flex space-x-2 mt-3">
              <button
                onClick={handlePreviousStep}
                disabled={currentStepIndex === 0}
                className="flex-1 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ⬅️ Previous Step
              </button>
              <button
                onClick={handleNextStep}
                disabled={currentStepIndex >= steps.length - 1}
                className="flex-1 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next Step ➡️
              </button>
            </div>

            {/* Allow moving to next step after at least one submission on this step OR if step is completed */}
            {((submitResult && submitResult.results?.length > 0) || isCurrentStepCompleted) && currentStepIndex < steps.length - 1 && (
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

function SubmissionModal({ project, onClose, token, onSuccess }) {
  const [file, setFile] = useState(null)
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [submissions, setSubmissions] = useState([])
  const [loadingSubmissions, setLoadingSubmissions] = useState(true)

  useEffect(() => {
    fetchSubmissions()
  }, [project.id])

  const fetchSubmissions = async () => {
    try {
      const submissionType = project.submissionType || 'project'
      const res = await fetch(`${API_URL}/api/projects/${project.id}/submissions?submission_type=${submissionType}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      const data = await res.json()
      if (data.success) {
        setSubmissions(data.submissions || [])
      }
    } catch (err) {
      console.error('Error fetching submissions:', err)
    } finally {
      setLoadingSubmissions(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file to upload')
      return
    }

    setSubmitting(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('notes', notes)
      formData.append('submission_type', project.submissionType || 'project')

      const res = await fetch(`${API_URL}/api/projects/${project.id}/submit`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          // Don't set Content-Type - browser will set it automatically with boundary for FormData
        },
        body: formData,
      })

      const data = await res.json()

      if (data.success) {
        setFile(null)
        setNotes('')
        await fetchSubmissions()
        if (onSuccess) onSuccess()
      } else {
        setError(data.error || 'Failed to submit project')
      }
    } catch (err) {
      console.error('Error submitting project:', err)
      setError('Network error. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDownload = async (submissionId) => {
    try {
      const res = await fetch(`${API_URL}/api/submissions/${submissionId}/download`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        const submission = submissions.find(s => s.id === submissionId)
        a.download = submission?.filename || 'download'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (err) {
      console.error('Error downloading file:', err)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-2xl font-bold mb-2">
              {project.submissionType === 'final_test' ? '🎯 Final Project Test: ' : 'Submit Project: '}{project.name}
            </h3>
            <p className="text-gray-600">
              {project.submissionType === 'final_test' 
                ? 'Upload your final project test/exam file' 
                : 'Upload your completed project file'}
            </p>
            {project.submissionType === 'final_test' && (
              <div className="mt-2 p-2 bg-purple-50 border border-purple-200 rounded text-sm text-purple-800">
                <strong>⚠️ Final Test:</strong> This is your final submission for evaluation. Make sure your work is complete.
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div>
            <label className="block mb-2 font-medium text-gray-700">
              Select File
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              className="w-full px-4 py-2 border rounded-lg"
              accept=".py,.txt,.pdf,.doc,.docx,.zip,.rar,.7z,.jpg,.jpeg,.png,.gif"
            />
            {file && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {file.name} ({formatFileSize(file.size)})
              </p>
            )}
          </div>

          <div>
            <label className="block mb-2 font-medium text-gray-700">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg"
              rows="3"
              placeholder="Add any notes about your submission..."
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-100 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || !file}
            className="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            {submitting ? 'Uploading...' : '📤 Submit Project'}
          </button>
        </form>

        <div className="border-t pt-4">
          <h4 className="font-bold text-lg mb-3">
            Your Previous {project.submissionType === 'final_test' ? 'Final Test' : 'Project'} Submissions
          </h4>
          {loadingSubmissions ? (
            <p className="text-gray-600">Loading...</p>
          ) : submissions.length === 0 ? (
            <p className="text-gray-600">No submissions yet</p>
          ) : (
            <div className="space-y-2">
              {submissions.map((submission) => (
                <div
                  key={submission.id}
                  className="border rounded-lg p-3 flex justify-between items-center"
                >
                  <div className="flex-1">
                    <p className="font-medium">{submission.filename}</p>
                    <p className="text-sm text-gray-600">
                      Submitted: {formatDate(submission.submitted_at)}
                      {submission.file_size && ` • ${formatFileSize(submission.file_size)}`}
                    </p>
                    {submission.notes && (
                      <p className="text-sm text-gray-500 mt-1">Notes: {submission.notes}</p>
                    )}
                    <div className="flex gap-2 mt-1">
                      {submission.submission_type === 'final_test' && (
                        <span className="inline-block px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                          🎯 Final Test
                        </span>
                      )}
                      {submission.status && (
                        <span className={`inline-block px-2 py-1 rounded text-xs ${
                          submission.status === 'approved' ? 'bg-green-100 text-green-800' :
                          submission.status === 'needs_revision' ? 'bg-yellow-100 text-yellow-800' :
                          submission.status === 'reviewed' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {submission.status}
                        </span>
                      )}
                    </div>
                    {submission.review_notes && (
                      <div className="mt-2 p-2 bg-blue-50 rounded text-sm">
                        <strong>Review:</strong> {submission.review_notes}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleDownload(submission.id)}
                    className="ml-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm"
                  >
                    Download
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function FinalProjectSubmissionModal({ onClose, token, onSuccess }) {
  const [file, setFile] = useState(null)
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [submissions, setSubmissions] = useState([])
  const [loadingSubmissions, setLoadingSubmissions] = useState(true)

  useEffect(() => {
    fetchSubmissions()
  }, [])

  const fetchSubmissions = async () => {
    try {
      const res = await fetch(`${API_URL}/api/final-project/submissions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      const data = await res.json()
      if (data.success) {
        setSubmissions(data.submissions || [])
      }
    } catch (err) {
      console.error('Error fetching final project submissions:', err)
    } finally {
      setLoadingSubmissions(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file to upload')
      return
    }

    setSubmitting(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('notes', notes)

      const res = await fetch(`${API_URL}/api/final-project/submit`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      const data = await res.json()

      if (data.success) {
        setFile(null)
        setNotes('')
        await fetchSubmissions()
        if (onSuccess) onSuccess()
      } else {
        setError(data.error || 'Failed to submit final project')
      }
    } catch (err) {
      console.error('Error submitting final project:', err)
      setError('Network error. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDownload = async (submissionId) => {
    try {
      const res = await fetch(`${API_URL}/api/submissions/${submissionId}/download`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        const submission = submissions.find(s => s.id === submissionId)
        a.download = submission?.filename || 'download'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (err) {
      console.error('Error downloading file:', err)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-2xl font-bold mb-2">🎯 Final Project Submission</h3>
            <p className="text-gray-600">Upload your final project work for evaluation</p>
            <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded text-sm text-purple-800">
              <strong>⚠️ Important:</strong> This is your final project submission. Make sure your work is complete and ready for evaluation.
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div>
            <label className="block mb-2 font-medium text-gray-700">
              Select File
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              className="w-full px-4 py-2 border rounded-lg"
              accept=".py,.txt,.pdf,.doc,.docx,.zip,.rar,.7z,.jpg,.jpeg,.png,.gif"
            />
            {file && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {file.name} ({formatFileSize(file.size)})
              </p>
            )}
          </div>

          <div>
            <label className="block mb-2 font-medium text-gray-700">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg"
              rows="3"
              placeholder="Add any notes about your final project submission..."
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-100 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || !file}
            className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
          >
            {submitting ? 'Uploading...' : '🎯 Submit Final Project'}
          </button>
        </form>

        <div className="border-t pt-4">
          <h4 className="font-bold text-lg mb-3">Your Previous Final Project Submissions</h4>
          {loadingSubmissions ? (
            <p className="text-gray-600">Loading...</p>
          ) : submissions.length === 0 ? (
            <p className="text-gray-600">No final project submissions yet</p>
          ) : (
            <div className="space-y-2">
              {submissions.map((submission) => (
                <div
                  key={submission.id}
                  className="border rounded-lg p-3 flex justify-between items-center"
                >
                  <div className="flex-1">
                    <p className="font-medium">{submission.filename}</p>
                    <p className="text-sm text-gray-600">
                      Submitted: {formatDate(submission.submitted_at)}
                      {submission.file_size && ` • ${formatFileSize(submission.file_size)}`}
                    </p>
                    {submission.notes && (
                      <p className="text-sm text-gray-500 mt-1">Notes: {submission.notes}</p>
                    )}
                    <div className="flex gap-2 mt-1">
                      <span className="inline-block px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                        🎯 Final Project
                      </span>
                      {submission.status && (
                        <span className={`inline-block px-2 py-1 rounded text-xs ${
                          submission.status === 'approved' ? 'bg-green-100 text-green-800' :
                          submission.status === 'needs_revision' ? 'bg-yellow-100 text-yellow-800' :
                          submission.status === 'reviewed' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {submission.status}
                        </span>
                      )}
                    </div>
                    {submission.review_notes && (
                      <div className="mt-2 p-2 bg-blue-50 rounded text-sm">
                        <strong>Review:</strong> {submission.review_notes}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleDownload(submission.id)}
                    className="ml-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm"
                  >
                    Download
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
