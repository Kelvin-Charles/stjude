import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'https://stjude.beetletz.online'

export default function ReadingResources() {
  const { token } = useAuth()
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedResource, setSelectedResource] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  useEffect(() => {
    fetchResources()
  }, [])

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
    } finally {
      setLoading(false)
    }
  }

  const categories = ['all', ...new Set(resources.map(r => r.category).filter(Boolean))]

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || resource.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  if (loading) {
    return <div className="text-white text-center py-8">Loading resources...</div>
  }

  return (
    <div className="mt-8">
      <h2 className="text-3xl font-bold text-white mb-6">📚 Reading Resources</h2>

      {/* Search and Filter */}
      <div className="bg-white rounded-xl p-4 shadow-lg mb-6">
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Search resources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredResources.length === 0 ? (
          <div className="col-span-full bg-white rounded-xl p-8 text-center">
            <p className="text-gray-600">
              {searchTerm || selectedCategory !== 'all' 
                ? 'No resources match your search.' 
                : 'No reading resources available yet. Check back later!'}
            </p>
          </div>
        ) : (
          filteredResources.map((resource) => (
            <div key={resource.id} className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-bold text-gray-800">{resource.title}</h3>
                {resource.category && (
                  <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                    {resource.category}
                  </span>
                )}
              </div>
              {resource.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{resource.description}</p>
              )}
              <div className="text-xs text-gray-500 mb-4">
                By {resource.creator_name || 'Mentor'} • {new Date(resource.created_at).toLocaleDateString()}
              </div>
              <button
                onClick={() => setSelectedResource(resource)}
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
              >
                Read More
              </button>
            </div>
          ))
        )}
      </div>

      {/* Resource Detail Modal */}
      {selectedResource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">{selectedResource.title}</h3>
                {selectedResource.category && (
                  <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                    {selectedResource.category}
                  </span>
                )}
              </div>
              <button
                onClick={() => setSelectedResource(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="text-sm text-gray-600 mb-4">
              By {selectedResource.creator_name || 'Mentor'} • {new Date(selectedResource.created_at).toLocaleDateString()}
            </div>

            {selectedResource.description && (
              <p className="text-gray-700 mb-4 italic">{selectedResource.description}</p>
            )}

            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                {selectedResource.content}
              </div>
            </div>

            <button
              onClick={() => setSelectedResource(null)}
              className="mt-6 w-full bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
