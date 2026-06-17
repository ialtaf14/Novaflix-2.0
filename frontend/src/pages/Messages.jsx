import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { io } from 'socket.io-client'
import { useAuthStore } from '../store/useAuthStore'
import api from '../services/api'
import './Messages.css'

const MOCK_GIFS = [
  "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3hicDcybmszdXJ2ZHB6M2g0Y2U4aHFycGg5cnFwbjZ6b3ozNmV4eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/L5aC2b3jA0880/giphy.gif",
  "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2F3OXFvYXpxeDV6bmF5bTF4N3Iyb2RseGV0dG9hNmN2dm15YWg3MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/y3x9rGLRSa4fe/giphy.gif",
  "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOW1hNDk3MXM2eG1oNnIxbHppOXJubm55MGJmczdzZHZudzhzMHZyeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/d10DmiIQotRtS/giphy.gif",
  "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjR6ZnF2azJqdnpia3Ixa3d3NWZ5MmNocWppZ3VibHR0MHpyam83OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/A8t748BfH69QA/giphy.gif"
]

export default function Messages() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuthStore()
  
  const [conversations, setConversations] = useState([])
  const [loadingConvs, setLoadingConvs] = useState(true)
  const [convError, setConvError] = useState('')
  const [activeConv, setActiveConv] = useState(null)
  const [messages, setMessages] = useState([])
  const [loadingMessages, setLoadingMessages] = useState(false)
  const [inputText, setInputText] = useState('')
  const [chatSearchQuery, setChatSearchQuery] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [showGifPicker, setShowGifPicker] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareMovieTitle, setShareMovieTitle] = useState('')
  const [replyingTo, setReplyingTo] = useState(null)
  
  const socketRef = useRef(null)
  const messagesEndRef = useRef(null)

  // Parse query parameters to see if we were passed a conversation user or movie share
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const shareUser = params.get('user')
    if (shareUser) {
      // Find or inject this user as active conversation
      api.get(`/users/public/${shareUser}`).then(r => {
        setActiveConv({
          username: r.data.username,
          name: r.data.name,
          photo_url: r.data.photo_url
        })
      }).catch(err => console.error("Load share user error:", err))
    }

    const movieParam = params.get('share_movie')
    if (movieParam) {
      setShareMovieTitle(movieParam)
    } else {
      setShareMovieTitle('')
    }
  }, [location.search])

  // Initialize socket connection
  useEffect(() => {
    if (!user) return
    
    // Connect to WebSocket server
    const socketUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || ''
    const socket = io(socketUrl, {
      path: '/ws/socket.io',
      auth: { username: user.username }
    })
    
    socketRef.current = socket
    
    socket.on('receive_message', (msg) => {
      // If message is for/from active conversation, append it
      if (
        (msg.sender === user.username && msg.receiver === activeConv?.username) ||
        (msg.sender === activeConv?.username && msg.receiver === user.username)
      ) {
        setMessages(prev => [...prev, msg])
        // Mark read
        api.post(`/chat/mark-read/${msg.id}`).catch(() => {})
      }
      
      // Refresh conversations list
      fetchConversations()
    })

    socket.on('data_update', (data) => {
      if (data.type === 'typing' && data.sender === activeConv?.username) {
        setIsTyping(true)
        setTimeout(() => setIsTyping(false), 2000)
      }
    })
    
    return () => {
      socket.disconnect()
    }
  }, [user, activeConv])

  useEffect(() => {
    fetchConversations()
  }, [])

  useEffect(() => {
    if (activeConv) {
      fetchMessages(activeConv.username)
    }
  }, [activeConv])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchConversations = async () => {
    setLoadingConvs(true)
    setConvError('')
    try {
      const { data } = await api.get('/chat/conversations')
      setConversations(data.conversations || [])
      if (!data.conversations?.length) {
        setConvError('')
      }
    } catch (err) {
      console.error("Load conversations failed:", err)
      setConvError('Could not load conversations. Make sure the backend is running.')
    } finally {
      setLoadingConvs(false)
    }
  }

  const fetchMessages = async (otherUser) => {
    setLoadingMessages(true)
    try {
      const { data } = await api.get(`/chat/${otherUser}`)
      setMessages(data.messages || [])
      await api.post(`/chat/mark-all-read/${otherUser}`).catch(() => {})
      fetchConversations()
    } catch (err) {
      console.error("Load chat history failed:", err)
      setMessages([])
    } finally {
      setLoadingMessages(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = (text = null, gifUrl = null) => {
    const content = text || gifUrl || inputText
    if (!content.trim() || !activeConv || !socketRef.current) return

    const msgPayload = {
      sender: user.username,
      receiver: activeConv.username,
      content: content.trim(),
      timestamp: Date.now(),
      reply_to: replyingTo ? replyingTo.id : null,
      type: gifUrl ? "gif" : "text"
    }

    socketRef.current.emit('send_message', msgPayload)
    
    // Optimistically update locally
    setMessages(prev => [...prev, {
      ...msgPayload,
      id: 'temp-' + Date.now(),
      sender_name: user.profile?.name || user.name || user.username,
      sender_photo: user.profile?.photo_url,
      reactions: {}
    }])
    
    setInputText('')
    setReplyingTo(null)
    setShowEmojiPicker(false)
    setShowGifPicker(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    } else {
      // Emit typing indicator
      socketRef.current?.emit('user_action', {
        type: 'typing',
        sender: user.username,
        receiver: activeConv?.username
      })
    }
  }

  const handleEmojiClick = (emoji) => {
    setInputText(prev => prev + emoji)
  }

  const handleAddReaction = async (msgId, emoji) => {
    try {
      await api.post(`/chat/${activeConv.username}/react/${msgId}`, { emoji })
      setMessages(prev => prev.map(m => {
        if (m.id === msgId) {
          const reactions = { ...(m.reactions || {}) }
          reactions[emoji] = [...(reactions[emoji] || [])]
          if (reactions[emoji].includes(user.username)) {
            reactions[emoji] = reactions[emoji].filter(u => u !== user.username)
          } else {
            reactions[emoji].push(user.username)
          }
          return { ...m, reactions }
        }
        return m
      }))
    } catch (err) {
      console.error("Reaction failed:", err)
    }
  }

  const filteredConversations = conversations.filter(c => {
    const name = (c.name || '').toLowerCase()
    const username = (c.username || '').toLowerCase()
    const q = chatSearchQuery.toLowerCase()
    return name.includes(q) || username.includes(q)
  })

  return (
    <div className="page messages-page-container fade-up">
      <div className="container messages-layout-box glass">
        
        {/* LEFT PANEL: Chats List */}
        <div className="messages-left-panel">
          <div className="left-panel-header">
            <button className="msg-back-btn" onClick={() => navigate(-1)} title="Go Back">
              ←
            </button>
            <h2>Chats</h2>
          </div>
          
          <div className="chat-search-wrap">
            <input
              type="text"
              className="chat-search-input"
              placeholder="Search messages..."
              value={chatSearchQuery}
              onChange={e => setChatSearchQuery(e.target.value)}
            />
          </div>

          <div className="conversations-list">
            {loadingConvs ? (
              <div className="chat-loading-state">
                <div className="chat-loading-spinner" />
                <span className="chat-loading-text">Loading conversations...</span>
              </div>
            ) : convError ? (
              <div className="conversations-error">{convError}</div>
            ) : filteredConversations.length === 0 ? (
              <div className="no-chats-msg">No conversations found. Start chatting from a user's profile!</div>
            ) : (
              filteredConversations.map(conv => (
                <div 
                  key={conv.username}
                  className={`conversation-item ${activeConv?.username === conv.username ? 'active' : ''}`}
                  onClick={() => setActiveConv(conv)}
                >
                  <img
                    src={conv.photo_url || 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'}
                    alt={conv.name}
                    className="conv-avatar"
                    onError={e => e.target.src = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'}
                  />
                  <div className="conv-details">
                    <div className="conv-top-row">
                      <span className="conv-name">{conv.name || conv.username}</span>
                      <span className="conv-time">
                        {conv.last_message_timestamp ? new Date(conv.last_message_timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''}
                      </span>
                    </div>
                    <div className="conv-bottom-row">
                      <p className="conv-preview">{conv.last_message || 'Start chatting!'}</p>
                      {conv.unread_count > 0 && (
                        <span className="conv-unread-badge">{conv.unread_count}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* RIGHT PANEL: Chat Conversation */}
        <div className="messages-right-panel">
          {activeConv ? (
            <>
              {/* Active Chat Header */}
              <div className="active-chat-header">
                <img
                  src={activeConv.photo_url || 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'}
                  alt={activeConv.name}
                  className="active-chat-avatar"
                  onError={e => e.target.src = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'}
                  onClick={() => navigate(`/user/${activeConv.username}`)}
                />
                <div className="active-chat-user-info" onClick={() => navigate(`/user/${activeConv.username}`)}>
                  <span className="active-chat-name">{activeConv.name || activeConv.username}</span>
                  <span className={`active-chat-status ${activeConv.online ? 'online' : 'offline'}`}>
                    {activeConv.online ? 'Online' : 'Offline'}
                  </span>
                </div>
                <div className="chat-header-actions">
                  <button className="chat-action-btn" title="Details" onClick={() => navigate(`/user/${activeConv.username}`)}>👤</button>
                </div>
              </div>

              {/* Chat Messages Log */}
              <div className="chat-messages-log">
                {loadingMessages ? (
                  <div className="chat-loading-state">
                    <div className="chat-loading-spinner" />
                    <span className="chat-loading-text">Loading messages...</span>
                  </div>
                ) : messages.length === 0 ? (
                  <div className="chat-loading-state">
                    <span style={{ fontSize: '2rem' }}>💬</span>
                    <span className="chat-loading-text">No messages yet. Say hello!</span>
                  </div>
                ) : messages.map(msg => (
                  <MessageBubble
                    key={msg.id}
                    msg={msg}
                    currentUser={user.username}
                    messages={messages}
                    onReact={(emoji) => handleAddReaction(msg.id, emoji)}
                    onReply={(m) => setReplyingTo(m)}
                  />
                ))}
                {isTyping && (
                  <div className="typing-indicator-bubble">
                    <span className="typing-dot">.</span>
                    <span className="typing-dot">.</span>
                    <span className="typing-dot">.</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Share Movie Preview Bar */}
              {shareMovieTitle && (
                <div className="chat-share-preview-bar animate-fade-in">
                  <span className="share-preview-text">
                    🎬 Share <strong>{shareMovieTitle}</strong> to this chat?
                  </span>
                  <div className="share-preview-actions">
                    <button 
                      className="share-preview-btn send" 
                      onClick={() => {
                        handleSendMessage(`[MOVIE_SHARE:${shareMovieTitle}]`)
                        navigate('/messages', { replace: true })
                      }}
                    >
                      Send Share
                    </button>
                    <button 
                      className="share-preview-btn cancel" 
                      onClick={() => navigate('/messages', { replace: true })}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Reply Preview Bar */}
              {replyingTo && (
                <div className="chat-reply-preview-bar">
                  <div className="reply-preview-details">
                    <span className="reply-title">Replying to {replyingTo.sender === user.username ? 'yourself' : `@${replyingTo.sender}`}</span>
                    <p className="reply-text-preview">{replyingTo.content.startsWith('[MOVIE_SHARE:') ? '🎬 Movie Share' : replyingTo.content}</p>
                  </div>
                  <button className="reply-cancel-btn" onClick={() => setReplyingTo(null)}>
                    &times;
                  </button>
                </div>
              )}

              {/* Chat Footer Input */}
              <div className="chat-footer-row">
                <button className="chat-plus-btn" title="Add GIF" onClick={() => { setShowGifPicker(!showGifPicker); setShowEmojiPicker(false); }}>
                  +
                </button>
                <button className="chat-emoji-btn" title="Add Emoji" onClick={() => { setShowEmojiPicker(!showEmojiPicker); setShowGifPicker(false); }}>
                  😊
                </button>
                <input
                  type="text"
                  className="chat-message-input"
                  placeholder="Type a message..."
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
                <button className="chat-send-btn" onClick={() => handleSendMessage()}>
                  ➔
                </button>

                {/* Emoji Picker Popover */}
                {showEmojiPicker && (
                  <div className="emoji-picker-popover glass">
                    {['👍', '❤️', '😂', '😮', '😢', '🙏', '🔥', '🎬', '🍿', '😮‍💨'].map(e => (
                      <span key={e} className="emoji-select-item" onClick={() => handleEmojiClick(e)}>
                        {e}
                      </span>
                    ))}
                  </div>
                )}

                {/* GIF Picker Popover */}
                {showGifPicker && (
                  <div className="gif-picker-popover glass">
                    {MOCK_GIFS.map((gif, index) => (
                      <img
                        key={index}
                        src={gif}
                        alt="gif option"
                        className="gif-select-item"
                        onClick={() => handleSendMessage(null, gif)}
                      />
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="chat-unselected-state">
              {shareMovieTitle ? (
                <>
                  <span style={{ fontSize: '3.5rem', marginBottom: '0.5rem' }}>🎬</span>
                  <h3>Share "{shareMovieTitle}"</h3>
                  <p style={{ color: '#ff61d2', fontWeight: 700, margin: '0 0 1.5rem 0' }}>Select a chat from the left panel to share this movie.</p>
                  <button className="share-preview-btn cancel" onClick={() => navigate('/messages', { replace: true })}>
                    Cancel Share
                  </button>
                </>
              ) : (
                <>
                  <span>💬</span>
                  <h3>Select a Conversation</h3>
                  <p>Choose an active thread from the left or search users to start chatting.</p>
                </>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

function MessageBubble({ msg, currentUser, messages, onReact, onReply }) {
  const isMine = msg.sender === currentUser
  const [movieDetails, setMovieDetails] = useState(null)
  const [movieLoadError, setMovieLoadError] = useState(false)
  const navigate = useNavigate()
  const isMovieShare = msg.content?.startsWith('[MOVIE_SHARE:')

  // Load movie details if it is a movie share
  useEffect(() => {
    if (isMovieShare) {
      const match = msg.content.match(/\[MOVIE_SHARE:(.*?)\]/)
      if (match && match[1]) {
        const title = match[1]
        api.get(`/movies/details?title=${encodeURIComponent(title)}`)
          .then(r => setMovieDetails(r.data))
          .catch(err => {
            console.error("Error fetching shared movie details:", err)
            setMovieLoadError(true)
          })
      }
    }
  }, [msg.content, isMovieShare])

  const handleAddWishlist = async (e, title) => {
    e.stopPropagation()
    try {
      await api.post('/users/wishlist', { title })
      alert(`${title} added to Wishlist!`)
    } catch (err) {
      console.error(err)
    }
  }

  const renderContent = () => {
    if (isMovieShare) {
      if (movieLoadError) {
        return <div className="chat-movie-share-card glass" style={{ padding: '1rem', color: '#ff4b2b' }}>⚠️ Movie details unavailable</div>
      }
      if (!movieDetails) {
        return <div className="chat-movie-share-card glass" style={{ padding: '1rem' }}>Loading movie details...</div>
      }
      return (
        <div className="chat-movie-share-card glass">
          <img 
            src={movieDetails.poster} 
            alt={movieDetails.title}
            onError={e => e.target.src = 'https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg'}
            className="share-movie-poster"
          />
          <div className="share-movie-details">
            <span className="share-movie-title">🎬 {movieDetails.title}</span>
            <span className="share-movie-meta">{movieDetails.year} • {movieDetails.genre?.split(', ')[0]} • {movieDetails.runtime}</span>
            <div className="share-ratings-row">
              <span className="imdb-pill">★ {movieDetails.rating || 'N/A'} IMDb</span>
              <span className="novaflix-pill">🟣 NovaFlix {movieDetails.novaflix_rating || 'N/A'}</span>
            </div>
            <div className="share-card-actions">
              <button onClick={() => navigate(`/movie?title=${encodeURIComponent(movieDetails.title)}`)} className="share-card-btn view">
                View Details
              </button>
              <button onClick={(e) => handleAddWishlist(e, movieDetails.title)} className="share-card-btn wishlist">
                + Wishlist
              </button>
            </div>
          </div>
        </div>
      )
    }

    if (msg.content.startsWith('http') && msg.content.includes('.gif')) {
      return <img src={msg.content} alt="shared gif" className="chat-shared-gif" />
    }

    return <p className="chat-bubble-text">{msg.content}</p>
  }

  const reactionsList = Object.keys(msg.reactions || {}).filter(k => msg.reactions[k]?.length > 0)
  const repliedMsg = msg.reply_to ? messages?.find(m => m.id === msg.reply_to) : null

  return (
    <div className={`message-bubble-wrapper ${isMine ? 'mine' : 'theirs'}`}>
      <div className="bubble-body-container">
        
        {/* Reply Quote bubble */}
        {repliedMsg && (
          <div className="chat-msg-reply-quote">
            <span className="reply-quote-sender">
              {repliedMsg.sender === currentUser ? 'You' : `@${repliedMsg.sender}`}
            </span>
            <p className="reply-quote-body">
              {repliedMsg.content.startsWith('[MOVIE_SHARE:') ? '🎬 Movie Share' : repliedMsg.content}
            </p>
          </div>
        )}

        {/* Render text, GIF, or movie share */}
        <div className={`message-bubble ${isMine ? 'mine' : 'theirs'}`}>
          {renderContent()}
          
          {/* Reaction Picker Overlay */}
          <div className="bubble-reaction-picker">
            {['❤️', '👍', '🔥', '😂'].map(emoji => (
              <span key={emoji} onClick={() => onReact(emoji)} className="reaction-trigger-emoji">
                {emoji}
              </span>
            ))}
            <span 
              onClick={() => onReply(msg)} 
              className="reaction-trigger-emoji reply-trigger" 
              title="Reply"
              style={{ borderLeft: '1px solid rgba(255,255,255,0.15)', paddingLeft: '6px', marginLeft: '2px' }}
            >
              ↩️
            </span>
          </div>
        </div>

        {/* Display Active Reactions */}
        {reactionsList.length > 0 && (
          <div className="bubble-reactions-row">
            {reactionsList.map(emoji => (
              <span key={emoji} className="bubble-reaction-badge" onClick={() => onReact(emoji)}>
                {emoji} <span className="react-count">{msg.reactions[emoji].length}</span>
              </span>
            ))}
          </div>
        )}
        
        <span className="message-timestamp">
          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          {isMine && <span className="seen-indicator"> • Seen</span>}
        </span>

      </div>
    </div>
  )
}
