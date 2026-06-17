import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import MovieCard from '../components/MovieCard'
import SkeletonCard from '../components/SkeletonCard'

export default function ActorDetails() {
  const [params] = useSearchParams()
  const name = params.get('name')
  const navigate = useNavigate()
  const [actor, setActor] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!name) return
    setLoading(true)
    api.get(`/movies/actor?name=${encodeURIComponent(name)}`)
      .then(r => setActor(r.data))
      .finally(() => setLoading(false))
  }, [name])

  if (loading) return (
    <div className="page"><div className="container">
      <div className="skeleton" style={{ height: 200, borderRadius: 18 }} />
    </div></div>
  )

  if (!actor) return <div className="page"><div className="container"><p>Actor not found.</p></div></div>

  return (
    <div className="page fade-up">
      <div className="container">
        <button className="btn btn-ghost" style={{ marginBottom: '1.5rem' }} onClick={() => navigate(-1)}>← Back</button>

        <div style={{ display: 'flex', gap: '2rem', marginBottom: '2.5rem', alignItems: 'flex-start' }}>
          <img src={actor.image} alt={actor.name}
            style={{ width: 180, height: 220, borderRadius: 16, objectFit: 'cover', flexShrink: 0,
                     boxShadow: '0 16px 40px rgba(0,0,0,0.6)' }}
            onError={e => e.target.src = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'} />
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: '0.5rem' }}>{actor.name}</h1>
            {actor.dob !== 'N/A' && (
              <p style={{ color: 'var(--muted)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                📅 Born: {actor.dob} {actor.age !== 'N/A' && `(Age ${actor.age})`}
              </p>
            )}
            {actor.country !== 'N/A' && (
              <p style={{ color: 'var(--muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>🌍 {actor.country}</p>
            )}
            <p style={{ color: 'rgba(255,255,255,0.75)', lineHeight: 1.7, fontSize: '0.9rem' }}>{actor.bio}</p>
          </div>
        </div>

        {actor.known_for?.length > 0 && (
          <>
            <h2 className="section-title">🎬 Known For</h2>
            <div className="movie-grid">
              {actor.known_for.map(t => <MovieCard key={t} title={t} poster={null} rating="N/A" year="N/A" />)}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
