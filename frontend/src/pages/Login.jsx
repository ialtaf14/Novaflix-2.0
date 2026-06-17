import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import api from '../services/api'
import PasswordInput from '../components/PasswordInput'
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
  const [signupStep, setSignupStep] = useState('details')
  const [signupForm, setSignupForm] = useState({ username: '', name: '', email: '', password: '', confirm: '' })
  const [signupEmail, setSignupEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [signupError, setSignupError] = useState('')
  const [signupLoading, setSignupLoading] = useState(false)
  const [devOtp, setDevOtp] = useState(null)
  const [resendTimer, setResendTimer] = useState(0)

  // ── Forgot password state ────────────────────────────────────────────────
  const [fpStep, setFpStep] = useState('username')   // 'username' | 'otp' | 'success'
  const [fpUsername, setFpUsername] = useState('')
  const [fpOtp, setFpOtp] = useState('')
  const [fpPassword, setFpPassword] = useState('')
  const [fpConfirm, setFpConfirm] = useState('')
  const [fpError, setFpError] = useState('')
  const [fpLoading, setFpLoading] = useState(false)
  const [fpDevOtp, setFpDevOtp] = useState(null)
  const [fpMaskedEmail, setFpMaskedEmail] = useState('')
  const [fpResendTimer, setFpResendTimer] = useState(0)

  // ── Helpers ──────────────────────────────────────────────────────────────
  const startResendTimer = (setter) => {
    setter(30)
    const interval = setInterval(() => {
      setter((t) => { if (t <= 1) { clearInterval(interval); return 0 } return t - 1 })
    }, 1000)
  }

  const switchTab = (t) => {
    setTab(t)
    setLoginError('')
    setSignupError('')
    setFpError('')
    setFpStep('username')
    setFpUsername('')
    setFpOtp('')
    setFpPassword('')
    setFpConfirm('')
    setFpDevOtp(null)
    setSignupStep('details')
    setOtp('')
    setDevOtp(null)
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
  const handleSignupInit = async (e) => {
    e.preventDefault()
    if (signupForm.password !== signupForm.confirm) { setSignupError('Passwords do not match'); return }
    setSignupLoading(true); setSignupError('')
    try {
      const { data } = await api.post('/auth/signup/init', {
        username: signupForm.username, name: signupForm.name,
        email: signupForm.email, password: signupForm.password,
      })
      setSignupEmail(signupForm.email)
      setDevOtp(data.dev_otp)
      setSignupStep('otp')
      startResendTimer(setResendTimer)
    } catch (err) {
      setSignupError(err.response?.data?.detail || 'Signup failed')
    } finally { setSignupLoading(false) }
  }

  const handleSignupVerify = async (e) => {
    e.preventDefault()
    setSignupLoading(true); setSignupError('')
    try {
      const { data } = await api.post('/auth/signup/verify', { email: signupEmail, otp })
      setAuth(data.user, data.token)
      navigate('/discover')
    } catch (err) {
      setSignupError(err.response?.data?.detail || 'Invalid OTP')
    } finally { setSignupLoading(false) }
  }

  const handleResendOtp = async () => {
    try {
      const { data } = await api.post('/auth/signup/resend-otp', { email: signupEmail, otp: '' })
      setDevOtp(data.dev_otp)
      startResendTimer(setResendTimer)
    } catch (err) {
      setSignupError(err.response?.data?.detail || 'Failed to resend OTP')
    }
  }

  // ── Forgot password ───────────────────────────────────────────────────────
  const handleFpInit = async (e) => {
    e.preventDefault()
    if (!fpUsername.trim()) { setFpError('Enter your username'); return }
    setFpLoading(true); setFpError('')
    try {
      const { data } = await api.post('/auth/forgot-password/init', { username: fpUsername.trim() })
      setFpMaskedEmail(data.masked_email || '')
      setFpDevOtp(data.dev_otp)
      setFpStep('otp')
      startResendTimer(setFpResendTimer)
    } catch (err) {
      setFpError(err.response?.data?.detail || 'Username not found')
    } finally { setFpLoading(false) }
  }

  const handleFpVerify = async (e) => {
    e.preventDefault()
    if (fpPassword !== fpConfirm) { setFpError('Passwords do not match'); return }
    if (fpPassword.length < 8)    { setFpError('Password must be at least 8 characters'); return }
    setFpLoading(true); setFpError('')
    try {
      await api.post('/auth/forgot-password/verify', {
        username: fpUsername.trim(),
        otp: fpOtp.trim(),
        new_password: fpPassword,
      })
      setFpStep('success')
    } catch (err) {
      setFpError(err.response?.data?.detail || 'Invalid OTP or error resetting password')
    } finally { setFpLoading(false) }
  }

  const handleFpResend = async () => {
    try {
      const { data } = await api.post('/auth/forgot-password/init', { username: fpUsername.trim() })
      setFpDevOtp(data.dev_otp)
      startResendTimer(setFpResendTimer)
    } catch (err) {
      setFpError(err.response?.data?.detail || 'Failed to resend OTP')
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="login-page">
      <div className="login-box glass fade-up">

        {/* Logo */}
        <div className="login-logo">
          <img src="/logo.jpg" alt="NovaFlix" className="login-logo-img" />
        </div>
        <p className="login-tagline">Experience the future of cinema.</p>

        {/* ── Tab switcher (hidden on forgot-password tab) ── */}
        {tab !== 'forgot' && (
          <div className="login-tabs">
            <button className={tab === 'login'  ? 'tab active' : 'tab'} onClick={() => switchTab('login')}>Sign In</button>
            <button className={tab === 'signup' ? 'tab active' : 'tab'} onClick={() => switchTab('signup')}>Sign Up</button>
          </div>
        )}

        {/* ══════════════ LOGIN ══════════════ */}
        {tab === 'login' && (
          <form onSubmit={handleLogin} className="login-form">
            <input className="input" placeholder="Username" value={loginForm.username}
              onChange={e => setLoginForm(f => ({ ...f, username: e.target.value }))} required />
            <PasswordInput placeholder="Password" value={loginForm.password}
              onChange={e => setLoginForm(f => ({ ...f, password: e.target.value }))} required />

            {loginError && <p className="form-error">{loginError}</p>}

            <button className="btn btn-primary" type="submit" disabled={loginLoading} style={{ width: '100%' }}>
              {loginLoading ? 'Signing in…' : 'Sign In'}
            </button>

            {/* Forgot password link */}
            <button type="button" className="forgot-link" onClick={() => switchTab('forgot')}>
              Forgot password?
            </button>
          </form>
        )}

        {/* ══════════════ SIGNUP — details ══════════════ */}
        {tab === 'signup' && signupStep === 'details' && (
          <form onSubmit={handleSignupInit} className="login-form">
            <input className="input" placeholder="Username (@handle)" value={signupForm.username}
              maxLength={30} onChange={e => setSignupForm(f => ({ ...f, username: e.target.value }))} required />
            <input className="input" placeholder="Display Name" value={signupForm.name}
              maxLength={30} onChange={e => setSignupForm(f => ({ ...f, name: e.target.value }))} required />
            <input className="input" type="email" placeholder="Email" value={signupForm.email}
              onChange={e => setSignupForm(f => ({ ...f, email: e.target.value }))} required />
            <PasswordInput placeholder="Password (min 8 chars)" value={signupForm.password}
              onChange={e => setSignupForm(f => ({ ...f, password: e.target.value }))} required />
            <PasswordInput placeholder="Confirm Password" value={signupForm.confirm}
              onChange={e => setSignupForm(f => ({ ...f, confirm: e.target.value }))} required />
            {signupError && <p className="form-error">{signupError}</p>}
            <button className="btn btn-primary" type="submit" disabled={signupLoading} style={{ width: '100%' }}>
              {signupLoading ? 'Sending OTP…' : 'Continue →'}
            </button>
          </form>
        )}

        {/* ══════════════ SIGNUP — OTP ══════════════ */}
        {tab === 'signup' && signupStep === 'otp' && (
          <form onSubmit={handleSignupVerify} className="login-form">
            <p className="otp-hint">A 6-digit code was sent to <strong>{signupEmail}</strong></p>
            {devOtp && <p className="dev-otp">🔧 Dev mode OTP: <strong>{devOtp}</strong></p>}
            <input className="input" placeholder="Enter 6-digit OTP" value={otp} maxLength={6}
              onChange={e => setOtp(e.target.value)} required />
            {signupError && <p className="form-error">{signupError}</p>}
            <button className="btn btn-primary" type="submit" disabled={signupLoading} style={{ width: '100%' }}>
              {signupLoading ? 'Verifying…' : 'Verify & Create Account'}
            </button>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
              <button type="button" className="btn btn-ghost" style={{ fontSize: '0.8rem' }}
                onClick={() => setSignupStep('details')}>← Edit Details</button>
              <button type="button" className="btn btn-ghost" style={{ fontSize: '0.8rem' }}
                onClick={handleResendOtp} disabled={resendTimer > 0}>
                {resendTimer > 0 ? `Resend (${resendTimer}s)` : 'Resend OTP'}
              </button>
            </div>
          </form>
        )}

        {/* ══════════════ FORGOT PASSWORD — username ══════════════ */}
        {tab === 'forgot' && fpStep === 'username' && (
          <form onSubmit={handleFpInit} className="login-form">
            <div className="fp-header">
              <span className="fp-icon">🔑</span>
              <h2 className="fp-title">Reset Password</h2>
              <p className="fp-sub">Enter your username and we'll send an OTP to your registered email.</p>
            </div>
            <input className="input" placeholder="Your username" value={fpUsername}
              onChange={e => setFpUsername(e.target.value)} required />
            {fpError && <p className="form-error">{fpError}</p>}
            <button className="btn btn-primary" type="submit" disabled={fpLoading} style={{ width: '100%' }}>
              {fpLoading ? 'Sending OTP…' : 'Send Reset OTP'}
            </button>
            <button type="button" className="forgot-link" onClick={() => switchTab('login')}>
              ← Back to Sign In
            </button>
          </form>
        )}

        {/* ══════════════ FORGOT PASSWORD — OTP + new password ══════════════ */}
        {tab === 'forgot' && fpStep === 'otp' && (
          <form onSubmit={handleFpVerify} className="login-form">
            <p className="otp-hint">
              OTP sent to <strong>{fpMaskedEmail || 'your email'}</strong>
            </p>
            {fpDevOtp && <p className="dev-otp">🔧 Dev mode OTP: <strong>{fpDevOtp}</strong></p>}
            <input className="input" placeholder="6-digit OTP" value={fpOtp} maxLength={6}
              onChange={e => setFpOtp(e.target.value)} required />
            <PasswordInput placeholder="New password (min 8 chars)" value={fpPassword}
              onChange={e => setFpPassword(e.target.value)} required />
            <PasswordInput placeholder="Confirm new password" value={fpConfirm}
              onChange={e => setFpConfirm(e.target.value)} required />
            {fpError && <p className="form-error">{fpError}</p>}
            <button className="btn btn-primary" type="submit" disabled={fpLoading} style={{ width: '100%' }}>
              {fpLoading ? 'Resetting…' : 'Reset Password'}
            </button>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
              <button type="button" className="btn btn-ghost" style={{ fontSize: '0.8rem' }}
                onClick={() => setFpStep('username')}>← Edit Username</button>
              <button type="button" className="btn btn-ghost" style={{ fontSize: '0.8rem' }}
                onClick={handleFpResend} disabled={fpResendTimer > 0}>
                {fpResendTimer > 0 ? `Resend (${fpResendTimer}s)` : 'Resend OTP'}
              </button>
            </div>
          </form>
        )}

        {/* ══════════════ FORGOT PASSWORD — success ══════════════ */}
        {tab === 'forgot' && fpStep === 'success' && (
          <div className="login-form" style={{ textAlign: 'center', gap: '1.25rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div className="success-icon">✅</div>
            <h2 style={{ fontWeight: 800 }}>Password Reset!</h2>
            <p style={{ color: 'var(--muted)', fontSize: '0.88rem' }}>
              Your password has been updated. You can now sign in with your new password.
            </p>
            <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => switchTab('login')}>
              Go to Sign In
            </button>
          </div>
        )}

      </div>
    </div>
  )
}
