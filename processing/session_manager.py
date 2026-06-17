"""
NovaFlix Session Manager
------------------------
Handles persistent server-side sessions so users stay logged in
across browser refreshes. Tokens are stored in sessions.json and
validated on every page load via st.query_params.
"""

import json
import os
import uuid
import time

_SESSIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'sessions.json')
_SESSION_TTL   = 7 * 24 * 3600   # 7 days in seconds


# ── I/O helpers ────────────────────────────────────────────────────────────────

def _load() -> dict:
    """Load sessions dict from disk (returns {} if missing/corrupt)."""
    try:
        if os.path.exists(_SESSIONS_FILE):
            with open(_SESSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(sessions: dict) -> None:
    """Persist sessions dict to disk atomically."""
    tmp = _SESSIONS_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2)
    os.replace(tmp, _SESSIONS_FILE)


# ── Public API ─────────────────────────────────────────────────────────────────

def create_session(username: str) -> str:
    """
    Create a new session for *username*, persist it, and return the token.
    Any previous sessions for this user are kept (multi-device support).
    """
    sessions = _load()
    _cleanup_expired_in(sessions)   # prune stale entries while we have the file open

    token = str(uuid.uuid4())
    sessions[token] = {
        'username':   username,
        'created_at': time.time(),
        'expires_at': time.time() + _SESSION_TTL,
    }
    _save(sessions)
    return token


def validate_session(token: str):
    """
    Validate *token*.
    Returns (username, None) on success, or None if invalid/expired.
    Transparently extends the TTL on successful validation (sliding window).
    """
    if not token:
        return None

    sessions = _load()
    entry = sessions.get(token)
    if not entry:
        return None

    if time.time() > entry['expires_at']:
        # Expired — remove and bail
        del sessions[token]
        _save(sessions)
        return None

    # Slide the expiry window forward so active users never get logged out
    entry['expires_at'] = time.time() + _SESSION_TTL
    _save(sessions)
    return entry['username']


def destroy_session(token: str) -> None:
    """Remove a specific session token (logout)."""
    if not token:
        return
    sessions = _load()
    if token in sessions:
        del sessions[token]
        _save(sessions)


def destroy_all_sessions(username: str) -> None:
    """Remove ALL sessions for *username* (log out all devices)."""
    sessions = _load()
    to_delete = [t for t, d in sessions.items() if d.get('username') == username]
    for t in to_delete:
        del sessions[t]
    _save(sessions)


def cleanup_expired() -> int:
    """Remove all expired sessions. Returns count removed."""
    sessions = _load()
    before = len(sessions)
    _cleanup_expired_in(sessions)
    _save(sessions)
    return before - len(sessions)


# ── Internal helper ─────────────────────────────────────────────────────────────

def _cleanup_expired_in(sessions: dict) -> None:
    """In-place removal of expired entries from *sessions* dict."""
    now = time.time()
    expired = [t for t, d in sessions.items() if now > d.get('expires_at', 0)]
    for t in expired:
        del sessions[t]
