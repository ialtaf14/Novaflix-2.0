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

class SignupInitRequest(BaseModel):
    username: str
    name: str
    email: str
    password: str
    avatar: str = "🎬"

class OTPVerifyRequest(BaseModel):
    email: str
    otp: str

class ForgotPasswordInitRequest(BaseModel):
    username: str

class ForgotPasswordVerifyRequest(BaseModel):
    username: str
    otp: str
    new_password: str


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


@router.post("/signup/init")
def signup_init(body: SignupInitRequest):
    """Validate fields and send OTP — account NOT created yet."""
    # Validate username
    valid, msg = user_auth.validate_username(body.username)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    users = user_auth.load_users()
    if body.username in users:
        raise HTTPException(status_code=400, detail="Username already taken.")

    # Validate password
    valid, msg = user_auth.validate_password_strength(body.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Check email uniqueness
    if user_auth.is_email_registered(body.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Generate & send OTP
    otp = email_service.generate_otp()
    success, message = email_service.send_otp_email(body.email, otp)

    _otp_store[body.email] = {
        "otp": otp,
        "expires_at": time.time() + 300,  # 5 min
        "pending": {
            "username": body.username,
            "name": body.name,
            "email": body.email,
            "password": body.password,
            "avatar": body.avatar,
        },
    }

    if not success and message != "SMTP_NOT_CONFIGURED":
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {message}")

    return {"detail": "OTP sent", "email": body.email, "dev_otp": otp if message == "SMTP_NOT_CONFIGURED" else None}


@router.post("/signup/verify")
def signup_verify(body: OTPVerifyRequest, request: Request):
    entry = _otp_store.get(body.email)
    if not entry:
        raise HTTPException(status_code=400, detail="No pending signup for this email.")
    if time.time() > entry["expires_at"]:
        del _otp_store[body.email]
        raise HTTPException(status_code=400, detail="OTP expired. Please sign up again.")
    if body.otp.strip() != entry["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    pending = entry["pending"]
    success, msg = user_auth.signup(
        pending["username"], pending["name"], pending["email"], pending["password"]
    )
    del _otp_store[body.email]

    if not success:
        raise HTTPException(status_code=400, detail=msg)

    user_agent = request.headers.get("user-agent", "Unknown")
    ip_address = request.headers.get("x-forwarded-for", request.client.host if request.client else "Unknown")
    
    session_id = session_manager.create_session(
        pending["username"],
        device="Browser",
        browser="Unknown" if not user_agent else user_agent[:20],
        os_name="Unknown",
        location="Unknown (Mock)",
        ip_address=ip_address
    )

    token = create_access_token({"sub": pending["username"], "session_id": session_id})
    users = user_auth.load_users()
    user_data = users[pending["username"]]
    return {
        "token": token,
        "user": {
            "username": pending["username"],
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "profile": user_data.get("profile", {}),
            "wishlist": [],
            "watched_list": [],
        },
    }


@router.post("/signup/resend-otp")
def signup_resend_otp(body: OTPVerifyRequest):
    entry = _otp_store.get(body.email)
    if not entry:
        raise HTTPException(status_code=400, detail="No pending signup.")
    otp = email_service.generate_otp()
    entry["otp"] = otp
    entry["expires_at"] = time.time() + 300
    success, message = email_service.send_otp_email(body.email, otp)
    return {"detail": "OTP resent", "dev_otp": otp if message == "SMTP_NOT_CONFIGURED" else None}


@router.post("/forgot-password/init")
def forgot_password_init(body: ForgotPasswordInitRequest):
    email = user_auth.get_user_email(body.username)
    if not email:
        raise HTTPException(status_code=404, detail="Username not found.")
    otp = email_service.generate_otp()
    success, message = email_service.send_otp_email(email, otp)
    _otp_store[f"reset:{body.username}"] = {
        "otp": otp,
        "expires_at": time.time() + 300,
        "email": email,
    }
    return {"detail": "Reset OTP sent", "masked_email": _mask_email(email),
            "dev_otp": otp if message == "SMTP_NOT_CONFIGURED" else None}


@router.post("/forgot-password/verify")
def forgot_password_verify(body: ForgotPasswordVerifyRequest):
    key = f"reset:{body.username}"
    entry = _otp_store.get(key)
    if not entry:
        raise HTTPException(status_code=400, detail="No reset request found.")
    if time.time() > entry["expires_at"]:
        del _otp_store[key]
        raise HTTPException(status_code=400, detail="OTP expired.")
    if body.otp.strip() != entry["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    valid, msg = user_auth.validate_password_strength(body.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    success, msg = user_auth.reset_password(body.username, body.new_password)
    del _otp_store[key]
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"detail": "Password reset successfully."}


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
