import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import api from '../services/api'
import PasswordInput from '../components/PasswordInput'
import { useGoogleLogin } from '@react-oauth/google'
import './Login.css'

export default function Login() {
  const [tab, setTab] = useState('login')
  const navigate = useNavigate()
  const location = useLocation()
  const { setAuth } = useAuthStore()
  const from = location.state?.from?.pathname || '/discover'

  // ── Login state ──────────────────────────────────────────────────────────
  const [loginForm, setLoginForm] = useState({ username: '', password: '' })
  const [loginError, setLoginError] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)

  // ── Signup state ─────────────────────────────────────────────────────────
  const [signupForm, setSignupForm] = useState({ username: '', name: '', password: '' })
  const [signupError, setSignupError] = useState('')
  const [signupLoading, setSignupLoading] = useState(false)

  // ── Helpers ──────────────────────────────────────────────────────────────
  const switchTab = (t) => {
    setTab(t)
    setLoginError('')
    setSignupError('')
  }

  // ── Login ─────────────────────────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginLoading(true); setLoginError('')
    try {
      const { data } = await api.post('/auth/login', loginForm)
      setAuth(data.user, data.token)
      navigate(from, { replace: true })
    } catch (err) {
      setLoginError(err.response?.data?.detail || 'Login failed')
    } finally { setLoginLoading(false) }
  }

  // ── Signup ────────────────────────────────────────────────────────────────
  const handleSignup = async (e) => {
    e.preventDefault()
    setSignupLoading(true); setSignupError('')
    try {
      const { data } = await api.post('/auth/signup', {
        username: signupForm.username,
        name: signupForm.name,
        password: signupForm.password,
      })
      setAuth(data.user, data.token)
      navigate('/discover')
    } catch (err) {
      setSignupError(err.response?.data?.detail || 'Signup failed')
    } finally { setSignupLoading(false) }
  }

  // ── Helper: Send OAuth data to backend ────────────────────────────────────
  const processOAuth = async (userData) => {
    setLoginLoading(true)
    setSignupLoading(true)
    setLoginError('')
    setSignupError('')
    try {
      const { data } = await api.post('/auth/oauth', userData)
      setAuth(data.user, data.token)
      navigate(from, { replace: true })
    } catch (err) {
      const msg = err.response?.data?.detail || 'OAuth login failed'
      setLoginError(msg)
      setSignupError(msg)
    } finally {
      setLoginLoading(false)
      setSignupLoading(false)
    }
  }

  // ── Official Google OAuth ─────────────────────────────────────────────────
  const loginWithGoogle = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        // Fetch real user info from Google using the access token
        const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` }
        })
        const u = await res.json()
        await processOAuth({
          username: u.email.split('@')[0].toLowerCase().replace(/[^a-z0-9]/g, ''),
          name: u.name,
          email: u.email,
          photo_url: u.picture,
          provider_id: `google-${u.sub}`
        })
      } catch {
        setLoginError('Google login failed')
        setSignupError('Google login failed')
        setLoginLoading(false)
        setSignupLoading(false)
      }
    },
    onError: () => {
      setLoginError('Google Sign In was cancelled')
      setSignupError('Google Sign In was cancelled')
    },
    flow: 'implicit',
    prompt: 'select_account'
  })

  // ── Official Facebook OAuth ───────────────────────────────────────────────
  const loginWithFacebook = () => {
    if (typeof window.FB === 'undefined') {
      setLoginError('Facebook SDK not loaded. Please provide a Facebook App ID.')
      setSignupError('Facebook SDK not loaded. Please provide a Facebook App ID.')
      return
    }
    window.FB.login((response) => {
      if (response.authResponse) {
        window.FB.api('/me', { fields: 'id,name,email,picture.width(200)' }, async (fbUser) => {
          await processOAuth({
            username: (fbUser.name || 'fbuser').toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/g, ''),
            name: fbUser.name,
            email: fbUser.email || '',
            photo_url: fbUser.picture?.data?.url || '',
            provider_id: `facebook-${fbUser.id}`
          })
        })
      } else {
        setLoginError('Facebook login was cancelled')
        setSignupError('Facebook login was cancelled')
      }
    }, { scope: 'public_profile' })
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="login-page">
      <div className="login-box glass fade-up">

        {/* Logo */}
        <div className="login-logo">
          <img src="/logo.jpg" alt="NovaFlix" className="login-logo-img" />
        </div>
        
        <div style={{textAlign: "center", marginBottom: "25px"}}>
          <h2 style={{color: "white", marginBottom: "8px", fontSize: "1.5rem"}}>
            {tab === 'login' ? 'Sign In' : 'Sign Up'}
          </h2>
          <p style={{color: "#aaa", fontSize: "0.9rem"}}>
            {tab === 'login' ? 'Welcome back! Please sign in to continue' : 'Create your account to get started'}
          </p>
        </div>

        {/* ══════════════ SIGN UP ══════════════ */}
        {tab === 'signup' && (
          <div className="login-form">
            <p className="section-title">1. Sign Up Manually</p>
            <form onSubmit={handleSignup} style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
              <div className="input-group">
                <i className="far fa-user input-icon"></i>
                <input className="input" placeholder="Username" value={signupForm.username}
                  maxLength={30} onChange={e => setSignupForm(f => ({ ...f, username: e.target.value }))} required />
              </div>
              <div className="input-group">
                <i className="far fa-id-badge input-icon"></i>
                <input className="input" placeholder="Name" value={signupForm.name}
                  maxLength={30} onChange={e => setSignupForm(f => ({ ...f, name: e.target.value }))} required />
              </div>
              <div className="input-group">
                <PasswordInput placeholder="Password" value={signupForm.password}
                  onChange={e => setSignupForm(f => ({ ...f, password: e.target.value }))} required />
              </div>
              
              {signupError && <p className="form-error">{signupError}</p>}
              
              <button className="btn btn-primary btn-full" type="submit" disabled={signupLoading}>
                {signupLoading ? 'Signing Up…' : 'Sign Up'}
              </button>
            </form>

            <div className="divider"><span>OR</span></div>

            <button type="button" className="btn btn-google" onClick={() => loginWithGoogle()} disabled={signupLoading}>
              <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" alt="G" />
              Sign Up with Google
            </button>
            <button type="button" className="btn btn-facebook" onClick={() => loginWithFacebook()} disabled={signupLoading}>
              <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png" alt="F" />
              Sign Up with Facebook
            </button>
            
            <p className="auth-switch">
              Already have an account? <span onClick={() => switchTab('login')}>Sign In</span>
            </p>
          </div>
        )}

        {/* ══════════════ LOGIN ══════════════ */}
        {tab === 'login' && (
          <div className="login-form">
            <p className="section-title">1. Sign In with Username</p>
            <form onSubmit={handleLogin} style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
              <div className="input-group">
                <i className="far fa-user input-icon"></i>
                <input className="input" placeholder="Username" value={loginForm.username}
                  onChange={e => setLoginForm(f => ({ ...f, username: e.target.value }))} required />
              </div>
              <div className="input-group">
                <PasswordInput placeholder="Password" value={loginForm.password}
                  onChange={e => setLoginForm(f => ({ ...f, password: e.target.value }))} required />
              </div>

              {loginError && <p className="form-error">{loginError}</p>}

              <button className="btn btn-primary btn-full" type="submit" disabled={loginLoading}>
                {loginLoading ? 'Signing in…' : 'Sign In'}
              </button>
            </form>

            <div className="divider"><span>OR</span></div>

            <button type="button" className="btn btn-google" onClick={() => loginWithGoogle()} disabled={loginLoading}>
              <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" alt="G" />
              Sign In with Google
            </button>
            <button type="button" className="btn btn-facebook" onClick={() => loginWithFacebook()} disabled={loginLoading}>
              <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png" alt="F" />
              Sign In with Facebook
            </button>

            <p className="auth-switch">
              Don't have an account? <span onClick={() => switchTab('signup')}>Sign Up</span>
            </p>
          </div>
        )}

      </div>
    </div>
  )
}
