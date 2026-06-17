"""
Enhanced chat store — per-conversation JSON storage with reactions,
seen-status, typing, movie cards, and conversation metadata.
"""
import json, os, time, uuid

try:
    from core.config import get_settings
    _base = os.path.dirname(get_settings().USERS_FILE)
except Exception:
    _base = os.path.join(os.path.dirname(__file__), '..', '..', 'Files')

CHAT_DB = os.path.join(_base, 'chats.json')
FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"

def load_chats() -> dict:
    if not os.path.exists(CHAT_DB):
        return {}
    with open(CHAT_DB, 'r') as f:
        try:
            data = json.load(f)
            # Support old list format
            if isinstance(data, list):
                return {}
            return data
        except json.JSONDecodeError:
            return {}

def save_chats(data: dict):
    os.makedirs(os.path.dirname(CHAT_DB), exist_ok=True)
    with open(CHAT_DB, 'w') as f:
        json.dump(data, f, indent=2)

def _conv_key(u1: str, u2: str) -> str:
    return "__".join(sorted([u1, u2]))

def get_conversation(user1: str, user2: str) -> list:
    chats = load_chats()
    key = _conv_key(user1, user2)
    msgs = chats.get(key, {}).get("messages", [])
    # Mark messages as seen for user1
    changed = False
    for m in msgs:
        if m.get("receiver") == user1 and not m.get("seen"):
            m["seen"] = True
            changed = True
    if changed:
        save_chats(chats)
    return msgs

def get_conversations_list(username: str) -> list:
    """Return all conversations this user is part of, sorted by latest message."""
    chats = load_chats()
    result = []
    for key, conv in chats.items():
        parts = key.split("__")
        if username not in parts:
            continue
        other = parts[0] if parts[1] == username else parts[1]
        msgs = conv.get("messages", [])
        last_msg = msgs[-1] if msgs else None
        unread = sum(1 for m in msgs if m.get("receiver") == username and not m.get("seen", False))
        content_preview = ""
        msg_timestamp = 0
        if last_msg:
            raw = last_msg.get("content", "")
            if raw.startswith("[MOVIE_SHARE:"):
                content_preview = "🎬 Shared a movie"
            elif raw.startswith("http") and (".gif" in raw or ".jpg" in raw or ".png" in raw):
                content_preview = "📷 Shared media"
            else:
                content_preview = raw[:80]
            msg_timestamp = last_msg.get("timestamp", 0)
        result.append({
            "username": other,
            "last_message": content_preview,
            "last_message_timestamp": msg_timestamp,
            "unread_count": unread,
            "pinned": conv.get("pinned_by", {}).get(username, False),
        })
    result.sort(key=lambda x: x["last_message_timestamp"] or 0, reverse=True)
    return result

def save_message(sender: str, receiver: str, content: str,
                 msg_type: str = "text", movie_data: dict = None,
                 reply_to: str = None) -> dict:
    chats = load_chats()
    key = _conv_key(sender, receiver)
    conv = chats.setdefault(key, {"messages": [], "pinned_by": {}})
    msg = {
        "id": str(uuid.uuid4()),
        "sender": sender,
        "receiver": receiver,
        "content": content,
        "type": msg_type,          # text | movie | image | gif
        "movie_data": movie_data,
        "reply_to": reply_to,
        "reactions": {},
        "seen": False,
        "deleted": False,
        "timestamp": int(time.time() * 1000)
    }
    conv["messages"].append(msg)
    save_chats(chats)
    return msg

def add_reaction(user1: str, user2: str, msg_id: str, reactor: str, emoji: str):
    chats = load_chats()
    key = _conv_key(user1, user2)
    for m in chats.get(key, {}).get("messages", []):
        if m["id"] == msg_id:
            if emoji:
                m["reactions"][reactor] = emoji
            else:
                m["reactions"].pop(reactor, None)
            break
    save_chats(chats)

def delete_message(user1: str, user2: str, msg_id: str, requester: str):
    chats = load_chats()
    key = _conv_key(user1, user2)
    for m in chats.get(key, {}).get("messages", []):
        if m["id"] == msg_id and m["sender"] == requester:
            m["deleted"] = True
            m["content"] = "This message was deleted"
            break
    save_chats(chats)

def delete_conversation(user1: str, user2: str):
    """Remove conversation between two users."""
    chats = load_chats()
    key = _conv_key(user1, user2)
    if key in chats:
        del chats[key]
        save_chats(chats)

def toggle_pin(user1: str, user2: str, requester: str):
    chats = load_chats()
    key = _conv_key(user1, user2)
    conv = chats.setdefault(key, {"messages": [], "pinned_by": {}})
    pb = conv.setdefault("pinned_by", {})
    pb[requester] = not pb.get(requester, False)
    save_chats(chats)

def seed_demo_messages(username: str, other_users: list):
    """Seed demo conversations so the Messages UI is populated."""
    chats = load_chats()
    existing_keys = set(chats.keys())
    if any(username in k for k in existing_keys):
        return

    if not other_users:
        return

    demo_convs = [
        {
            "other": other_users[0],
            "messages": [
                {"role": "other", "content": "Hey! 👋 Have you seen Interstellar?"},
                {"role": "me", "content": "Yes! One of my all time favorites! 💙"},
                {"role": "other", "content": "Same here! It's a masterpiece.."},
                {"role": "me", "content": "Added to my watchlist! Thanks 😊",
                 "type": "movie", "movie_data": {
                    "title": "Interstellar", "year": "2014", "rating": "8.6",
                    "genre": "Sci-Fi, Adventure, Drama",
                    "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMTEtYTVmZDEwNjQ2MzM3XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg"
                }},
            ]
        }
    ]

    t = int(time.time() * 1000)
    for ci, dc in enumerate(demo_convs):
        other = dc["other"]
        key = _conv_key(username, other)
        if key in chats:
            continue
        msgs = []
        for i, m in enumerate(dc["messages"]):
            sender = username if m["role"] == "me" else other
            receiver = other if m["role"] == "me" else username
            msgs.append({
                "id": str(uuid.uuid4()),
                "sender": sender,
                "receiver": receiver,
                "content": m["content"],
                "type": m.get("type", "text"),
                "movie_data": m.get("movie_data"),
                "reply_to": None,
                "reactions": {},
                "seen": True,
                "deleted": False,
                "timestamp": t - (len(dc["messages"]) - i) * 60000
            })
        chats[key] = {"messages": msgs, "pinned_by": {}}

    save_chats(chats)
