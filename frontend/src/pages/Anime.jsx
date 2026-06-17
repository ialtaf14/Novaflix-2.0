import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SeriesAnimeCard from '../components/SeriesAnimeCard';
import './Anime.css';

const API_BASE_URL = "/api";

const Anime = () => {
  const navigate = useNavigate();
  const [animeList, setAnimeList] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [selectedLetter, setSelectedLetter] = useState('All');
  const [selectedGenre, setSelectedGenre] = useState('All');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const letters = ['All', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')];
  const genres = ['All', 'Action', 'Drama', 'Comedy', 'Sci-Fi', 'Fantasy', 'Romance', 'Thriller', 'Animation'];

  useEffect(() => {
    fetchAnime();
  }, [selectedLetter, selectedGenre, page]);

  const fetchAnime = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/anime/browse?page=${page}&letter=${selectedLetter}&genre=${selectedGenre}`);
      if (res.ok) {
        const data = await res.json();
        setAnimeList(data.anime || []);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error("Error fetching anime:", err);
    }
    setLoading(false);
  };

  return (
    <div className="anime-page">
      <div className="anime-header">
        <h1>Anime Collection</h1>
        <p>Explore the best anime movies and series.</p>
      </div>

      <div className="anime-filters">
        <div className="filter-group">
          <label>Alphabetical:</label>
          <div className="letter-picker">
            {letters.map(l => (
              <button 
                key={l} 
                className={selectedLetter === l ? 'active' : ''}
                onClick={() => { setSelectedLetter(l); setPage(1); }}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label>Genre:</label>
          <select 
            value={selectedGenre} 
            onChange={(e) => { setSelectedGenre(e.target.value); setPage(1); }}
          >
            {genres.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">Loading Anime...</div>
      ) : (
        <>
          <div className="anime-grid">
            {animeList.length > 0 ? (
              animeList.map((anime, idx) => (
                <SeriesAnimeCard
                  key={idx}
                  {...anime}
                  type="anime"
                />
              ))
            ) : (
              <div className="no-results">No anime found matching your criteria.</div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</button>
              <span>Page {page} of {totalPages}</span>
              <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Anime;
