import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import SkeletonCard from "../components/SkeletonCard";
import SeriesAnimeCard from "../components/SeriesAnimeCard";
import "./Series.css";

function Series() {
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [letterFilter, setLetterFilter] = useState("All");
  const [genreFilter, setGenreFilter] = useState("All");

  const letters = ["All", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ".split(""), "#"];
  const genres = ["All", "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Mystery", "Romance", "Sci-Fi", "Thriller"];

  useEffect(() => {
    setLoading(true);
    fetch(`/api/series/browse?page=${page}&letter=${letterFilter}&genre=${genreFilter}`)
      .then((res) => res.json())
      .then((data) => {
        setSeries(data.series || []);
        setTotalPages(data.total_pages || 1);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching series:", err);
        setLoading(false);
      });
  }, [page, letterFilter, genreFilter]);

  return (
    <div className="series-page animate-fade-in">
      <div className="series-header">
        <h1>TV Series</h1>
        <p>Discover the best shows from Hollywood, India, and beyond.</p>
      </div>

      <div className="filters-container">
        <div className="filter-group">
          <label>Alphabetical:</label>
          <div className="animated-input-box">
            <input 
              type="text" 
              maxLength="1" 
              placeholder="Type A-Z..."
              value={letterFilter === 'All' ? '' : letterFilter}
              onChange={(e) => {
                const val = e.target.value.toUpperCase();
                if (/^[A-Z]$/.test(val)) {
                  setLetterFilter(val);
                } else {
                  setLetterFilter('All');
                }
                setPage(1);
              }}
            />
          </div>
        </div>

        <div className="filter-group">
          <label>Genre:</label>
          <div className="animated-select-box">
            <select 
              value={genreFilter} 
              onChange={(e) => {
                setGenreFilter(e.target.value);
                setPage(1);
              }}
            >
              {genres.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="movies-grid">
          {Array.from({ length: 15 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : series.length > 0 ? (
        <div className="movies-grid">
          {series.map((s, idx) => (
            <SeriesAnimeCard 
              key={idx}
              {...s}
              type="series"
            />
          ))}
        </div>
      ) : (
        <div className="no-results">
          <h2>No series found</h2>
          <p>Try changing your filters to see more results.</p>
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="page-btn"
          >
            <i className="fas fa-chevron-left"></i> Prev
          </button>
          <span className="page-info">
            Page <span className="current-page">{page}</span> of {totalPages}
          </span>
          <button
            disabled={page === totalPages}
            onClick={() => setPage(p => p + 1)}
            className="page-btn"
          >
            Next <i className="fas fa-chevron-right"></i>
          </button>
        </div>
      )}
    </div>
  );
}

export default Series;
