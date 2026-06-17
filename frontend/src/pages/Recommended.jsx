import { useState, useEffect } from 'react'
import api from '../services/api'
import MovieCard from '../components/MovieCard'

export default function Recommended() {
  const [collections, setCollections] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pageMap, setPageMap] = useState({}) // track page per collection
  const [loadingMore, setLoadingMore] = useState({})

  useEffect(() => {
    setLoading(true)
    api.get('/movies/recommended-page')
      .then(res => {
        setCollections(res.data.collections)
        // Initialize page map
        const pMap = {}
        res.data.collections.forEach(col => {
          pMap[col.id] = 1
        })
        setPageMap(pMap)
      })
      .catch(err => {
        console.error(err)
        setError('Failed to load recommended collections. Make sure you have watched some movies.')
      })
      .finally(() => setLoading(false))
  }, [])

  const handleShowMore = async (colId, colType, query) => {
    const currentPage = pageMap[colId] || 1
    const nextPage = currentPage + 1

    setLoadingMore(prev => ({ ...prev, [colId]: true }))
    try {
      const res = await api.get(`/movies/collection?col_type=${colType}&query=${encodeURIComponent(query)}&page=${nextPage}`)
      const newMovies = res.data.movies
      
      setCollections(prev => prev.map(col => {
        if (col.id === colId) {
          // Prevent duplicates just in case
          const existingIds = new Set(col.movies.map(m => m.title))
          const uniqueNewMovies = newMovies.filter(m => !existingIds.has(m.title))
          return { ...col, movies: [...col.movies, ...uniqueNewMovies] }
        }
        return col
      }))
      setPageMap(prev => ({ ...prev, [colId]: nextPage }))
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingMore(prev => ({ ...prev, [colId]: false }))
    }
  }

  if (loading) {
    return (
      <div className="page container fade-up" style={{ textAlign: 'center', marginTop: '5rem' }}>
        <div className="spinner"></div> Loading your personalized recommendations...
      </div>
    )
  }

  if (error) {
    return (
      <div className="page container fade-up" style={{ textAlign: 'center', marginTop: '5rem' }}>
        <h2 style={{ color: 'var(--red)' }}>{error}</h2>
        <p style={{ color: 'var(--muted)' }}>Try watching or adding movies to your wishlist first.</p>
      </div>
    )
  }

  if (collections.length === 0) {
    return (
      <div className="page container fade-up" style={{ textAlign: 'center', marginTop: '5rem' }}>
        <h2>No Recommendations Yet</h2>
        <p style={{ color: 'var(--muted)' }}>Watch or wishlist some movies to start getting personalized recommendations!</p>
      </div>
    )
  }

  return (
    <div className="page container fade-up recommended-page">
      <div className="recommended-header">
        <h1 className="section-title" style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Recommended Movies</h1>
        <p style={{ color: 'var(--muted)', fontSize: '1.1rem', marginBottom: '3rem' }}>
          Personalized suggestions based on your watched movies and preferences.
        </p>
      </div>

      <div className="collections-container">
        {collections.map(col => (
          <div key={col.id} className="collection-section">
            <div className="collection-header">
              <h2 className="collection-title">{col.title}</h2>
              {col.type === 'franchise' && <span className="collection-badge">Franchise</span>}
              {col.type === 'director' && <span className="collection-badge">Director</span>}
              {col.type === 'cast' && <span className="collection-badge">Cast</span>}
              {col.type === 'genre' && <span className="collection-badge">Genre</span>}
              {col.type === 'similar' && <span className="collection-badge">Recommended for You</span>}
            </div>

            <div className="movie-row">
              {col.movies.map(m => (
                <MovieCard key={m.title} {...m} />
              ))}
              {/* Show More Card */}
              {col.movies.length >= 15 && (
                <div 
                  className="show-more-card" 
                  onClick={() => handleShowMore(col.id, col.type, col.query)}
                >
                  {loadingMore[col.id] ? (
                    <div className="spinner" style={{ width: 30, height: 30, borderWidth: 3 }}></div>
                  ) : (
                    <>
                      <span style={{ fontSize: '2rem' }}>+</span>
                      <span>Show More</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
