"""
Auth router — login, signup (with OTP), forgot password, token validation.
"""
import time
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from core.auth import create_access_token
from core.deps import get_current_user
from fastapi import Depends
from processing import auth as user_auth
from processing import email_service
from processing import session_manager

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory OTP store: { email: {otp, expires_at, data} }
_otp_store: dict = {}


# ── Models ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    name: str
    password: str

class OAuthRequest(BaseModel):
    username: str
    name: str
    email: str
    photo_url: str
    provider_id: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login")
def login(body: LoginRequest, request: Request):
    success, result = user_auth.login(body.username, body.password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
        
    user_agent = request.headers.get("user-agent", "Unknown")
    ip_address = request.headers.get("x-forwarded-for", request.client.host if request.client else "Unknown")
    
    # Very basic user agent parsing
    browser = "Unknown"
    os_name = "Unknown"
    if "Firefox" in user_agent: browser = "Firefox"
    elif "Chrome" in user_agent: browser = "Chrome"
    elif "Safari" in user_agent: browser = "Safari"
    elif "Edge" in user_agent: browser = "Edge"
    
    if "Windows" in user_agent: os_name = "Windows"
    elif "Mac" in user_agent: os_name = "macOS"
    elif "Linux" in user_agent: os_name = "Linux"
    elif "Android" in user_agent: os_name = "Android"
    elif "iPhone" in user_agent or "iPad" in user_agent: os_name = "iOS"
        
    session_id = session_manager.create_session(
        body.username, 
        device="Browser", # simplified
        browser=browser, 
        os_name=os_name, 
        location="Unknown (Mock)", # Mock location
        ip_address=ip_address
    )
    
    token = create_access_token({"sub": body.username, "session_id": session_id})
    return {
        "token": token,
        "user": {
            "username": body.username,
            "name": result.get("name"),
            "email": result.get("email"),
            "profile": result.get("profile", {}),
            "wishlist": result.get("wishlist", []),
            "watched_list": result.get("watched_list", []),
        },
    }


@router.post("/signup")
def signup(body: SignupRequest, request: Request):
    """Direct signup with no email verification"""
    # Validate username
    valid, msg = user_auth.validate_username(body.username)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Validate password
    valid, msg = user_auth.validate_password_strength(body.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    success, msg = user_auth.signup(body.username, body.name, body.password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)

    # Automatically log them in after signup
    return login(LoginRequest(username=body.username, password=body.password), request)


@router.post("/oauth")
def oauth_handler(body: OAuthRequest, request: Request):
    """Handles Google and Facebook OAuth logins/signups"""
    # Use email prefix for username if not provided or generate one
    base_username = body.username or body.email.split("@")[0].lower()
    # To ensure uniqueness, we could append random numbers, but for simplicity we'll just trust the frontend's provided username
    
    success, result = user_auth.oauth_login(
        username=body.username,
        name=body.name,
        email=body.email,
        photo_url=body.photo_url,
        provider_id=body.provider_id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="OAuth login failed")
        
    user_agent = request.headers.get("user-agent", "Unknown")
    ip_address = request.headers.get("x-forwarded-for", request.client.host if request.client else "Unknown")
    
    session_id = session_manager.create_session(
        body.username,
        device="Browser",
        browser="Unknown" if not user_agent else user_agent[:20],
        os_name="Unknown",
        location="Unknown (OAuth)",
        ip_address=ip_address
    )

    token = create_access_token({"sub": body.username, "session_id": session_id})
    return {
        "token": token,
        "user": {
            "username": body.username,
            "name": result.get("name"),
            "email": result.get("email"),
            "profile": result.get("profile", {}),
            "wishlist": result.get("wishlist", []),
            "watched_list": result.get("watched_list", []),
        },
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    udata = current_user["data"]
    return {
        "username": current_user["username"],
        "name": udata.get("name"),
        "email": udata.get("email"),
        "profile": udata.get("profile", {}),
        "wishlist": udata.get("wishlist", []),
        "watched_list": udata.get("watched_list", []),
    }

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    session_id = current_user["session_id"]
    session_manager.revoke_session(session_id)
    return {"detail": "Logged out successfully"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_email(email: str) -> str:
    parts = email.split("@")
    u = parts[0]
    n = len(u)
    if n <= 1:
        masked = "*"
    elif n == 2:
        masked = u[0] + "*"
    else:
        masked = u[0] + "*" * (n - 2) + u[-1]
    return f"{masked}@{parts[1]}"
