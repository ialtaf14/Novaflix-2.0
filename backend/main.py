"""
NovaFlix FastAPI Backend
------------------------
Run: uvicorn main:app --reload --port 8000
"""
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from core.config import get_settings
from routers import auth, movies, users, chat, notifications, social, series, anime

settings = get_settings()

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="NovaFlix API", version="2.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(social.router)
app.include_router(series.router)
app.include_router(anime.router)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── SPA Static Files Serving ──────────────────────────────────────────────────
from fastapi import HTTPException
class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            raise ex

dist_dir = os.path.join(os.path.dirname(__file__), "dist")
if os.path.exists(dist_dir):
    app.mount("/", SPAStaticFiles(directory=dist_dir, html=True), name="frontend")

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# ── Socket.IO (real-time) ─────────────────────────────────────────────────────
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.ALLOWED_ORIGINS,
)

# Track connected users: { username: set(sid) }
_connected: dict = {}
_sid_to_user: dict = {}


@sio.event
async def connect(sid, environ, auth_data):
    username = (auth_data or {}).get("username", "anonymous")
    _sid_to_user[sid] = username
    
    if username not in _connected:
        _connected[username] = set()
    _connected[username].add(sid)
    
    print(f"[WS] {username} connected ({sid})")


@sio.event
async def disconnect(sid):
    user = _sid_to_user.pop(sid, "unknown")
    if user in _connected:
        _connected[user].discard(sid)
        if not _connected[user]:
            del _connected[user]
    print(f"[WS] {user} disconnected ({sid})")


@sio.event
async def user_action(sid, data):
    """
    Client emits {type: 'wishlist_add'|'wishlist_remove'|'watched_add'|'watched_remove',
                   username, title}
    We broadcast to ALL connected clients so they can refresh their state.
    """
    await sio.emit("data_update", data)


import time
import uuid
from processing import chat_store

@sio.event
async def send_message(sid, data):
    """
    Client emits {sender, receiver, content, timestamp, reply_to, type, movie_data}
    """
    sender = data.get("sender")
    receiver = data.get("receiver")
    content = data.get("content")
    reply_to = data.get("reply_to")
    msg_type = data.get("type", "text")
    movie_data = data.get("movie_data")
    
    if sender and receiver and content:
        # Save to store
        msg = chat_store.save_message(
            sender=sender, 
            receiver=receiver, 
            content=content,
            msg_type=msg_type,
            movie_data=movie_data,
            reply_to=reply_to
        )
        
        # Emit to receiver if online
        receiver_sids = _connected.get(receiver, set())
        for rsid in receiver_sids:
            await sio.emit("receive_message", msg, to=rsid)
            
        # Emit to sender's other sessions if any
        sender_sids = _connected.get(sender, set())
        for ssid in sender_sids:
            if ssid != sid:
                await sio.emit("receive_message", msg, to=ssid)


@sio.event
async def join_party(sid, data):
    room_code = data.get("room_code")
    username = _sid_to_user.get(sid, "anonymous")
    if room_code:
        sio.enter_room(sid, f"party_{room_code}")
        print(f"[WS] User {username} joined party room {room_code}")
        await sio.emit("party_user_joined", {"username": username}, room=f"party_{room_code}")


@sio.event
async def party_control(sid, data):
    """
    data contains: {room_code, action: 'play'|'pause'|'seek', progress}
    """
    room_code = data.get("room_code")
    action = data.get("action")
    progress = data.get("progress", 0)
    
    if room_code:
        from routers import social as social_router
        db = social_router.load_db(social_router.PARTIES_DB)
        parties = db.get("parties", {})
        if room_code in parties:
            parties[room_code]["playback_state"] = {
                "is_playing": (action == "play"),
                "progress": progress,
                "last_updated": int(time.time())
            }
            social_router.save_db(social_router.PARTIES_DB, db)
            
        await sio.emit("party_control_sync", {
            "action": action,
            "progress": progress,
            "sender": _sid_to_user.get(sid, "anonymous")
        }, room=f"party_{room_code}", skip_sid=sid)


@sio.event
async def party_chat_send(sid, data):
    room_code = data.get("room_code")
    text = data.get("text")
    username = _sid_to_user.get(sid, "anonymous")
    
    if room_code and text:
        from core import user_auth
        users = user_auth.load_users()
        udata = users.get(username, {})
        name = udata.get("name", username)
        photo_url = udata.get("profile", {}).get("photo_url") or "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"
        
        msg_obj = {
            "id": str(uuid.uuid4()),
            "username": username,
            "name": name,
            "photo_url": photo_url,
            "text": text,
            "timestamp": int(time.time())
        }
        
        from routers import social as social_router
        db = social_router.load_db(social_router.PARTIES_DB)
        parties = db.get("parties", {})
        if room_code in parties:
            parties[room_code].setdefault("chat", []).append(msg_obj)
            social_router.save_db(social_router.PARTIES_DB, db)
            
        await sio.emit("party_chat_message", msg_obj, room=f"party_{room_code}")


@sio.event
async def party_reaction_send(sid, data):
    room_code = data.get("room_code")
    emoji = data.get("emoji")
    username = _sid_to_user.get(sid, "anonymous")
    
    if room_code and emoji:
        await sio.emit("party_reaction_burst", {
            "username": username,
            "emoji": emoji
        }, room=f"party_{room_code}")



# ── Mount Socket.IO on /ws ────────────────────────────────────────────────────
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/ws/socket.io")

# The ASGI app that uvicorn actually serves
application = socket_app
