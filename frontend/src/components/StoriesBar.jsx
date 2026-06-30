import React from 'react';
import { useNavigate } from 'react-router-dom';
import './StoriesBar.css';

export default function StoriesBar({ stories, currentUser, onAddStory }) {
  const navigate = useNavigate();

  // Find if current user has an active story
  const currentUserStory = stories.find(g => g.username === currentUser?.username);
  
  // Exclude current user from the main list so we can pin them to the front
  const otherStories = stories.filter(g => g.username !== currentUser?.username);

  const handleStoryClick = (username) => {
    navigate(`/story-viewer?user=${username}`);
  };

  return (
    <div className="stories-bar-container">
      {/* 1. Logged-in User's "Your Story" Badge */}
      <div 
        className="story-circle-wrapper" 
        onClick={() => {
          if (currentUserStory) {
            handleStoryClick(currentUser.username);
          } else {
            onAddStory();
          }
        }}
      >
        <div className={`story-circle-outer ${currentUserStory ? (currentUserStory.has_new ? 'unviewed' : 'viewed') : 'none'}`}>
          <div className="story-circle-inner">
            <img 
              src={currentUser?.photo_url || currentUser?.avatar || 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'} 
              alt="Your Story" 
              className="story-circle-img"
              onError={(e) => { e.target.src = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png' }}
            />
          </div>
          {/* Show the blue '+' if the user has NO active stories */}
          {!currentUserStory && (
            <div className="story-add-badge">
              +
            </div>
          )}
        </div>
        <span className="story-username">Your story</span>
      </div>

      {/* 2. Other Users' Stories */}
      {otherStories.map(group => {
        const isUnviewed = group.has_new !== false; // default to true if undefined
        return (
          <div 
            key={group.username} 
            className="story-circle-wrapper" 
            onClick={() => handleStoryClick(group.username)}
          >
            <div className={`story-circle-outer ${isUnviewed ? 'unviewed' : 'viewed'}`}>
              <div className="story-circle-inner">
                <img 
                  src={group.photo_url || group.avatar || 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'} 
                  alt={group.username} 
                  className="story-circle-img"
                  onError={(e) => { e.target.src = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png' }}
                />
              </div>
            </div>
            <span className="story-username">
              {group.username.length > 10 ? group.username.slice(0, 9) + '…' : group.username}
            </span>
          </div>
        );
      })}
    </div>
  );
}
