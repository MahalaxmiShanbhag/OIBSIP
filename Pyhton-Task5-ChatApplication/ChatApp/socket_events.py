"""
socket_events.py
-----------------
All Flask-SocketIO event handlers for real-time chat functionality:

    connect / disconnect
    join    / leave
    send_message / receive_message
    typing  / stop_typing

Handlers are registered on a shared `socketio` instance via
`register_socket_events(socketio, db)` which is called once from app.py.
This keeps app.py free of clutter while still allowing the handlers to
access the Flask app/session context.
"""

from flask import session
from flask_socketio import join_room, leave_room, emit
from datetime import datetime

from models import db, Room, Message, User
from utils.emoji import convert_emoji_shortcodes

# Tracks how many currently-connected sockets are in each room.
# Structure: { room_name: {"count": int, "usernames": set(str)} }
_room_state = {}


def _get_room_bucket(room_name):
    """Return (and lazily create) the tracking bucket for a room."""
    if room_name not in _room_state:
        _room_state[room_name] = {"usernames": set()}
    return _room_state[room_name]


def register_socket_events(socketio):
    """Attach all Socket.IO event handlers to the given socketio instance."""

    @socketio.on("connect")
    def handle_connect():
        """Fired whenever a browser tab establishes a socket connection."""
        username = session.get("username")
        if username:
            print(f"[socket] {username} connected.")

    @socketio.on("disconnect")
    def handle_disconnect():
        """
        Fired when a socket disconnects (tab closed, refresh, network loss).
        We do a best-effort cleanup: remove the user from any room bucket
        we can find them in and notify that room they left.
        """
        username = session.get("username")
        if not username:
            return

        for room_name, bucket in list(_room_state.items()):
            if username in bucket["usernames"]:
                bucket["usernames"].discard(username)
                emit(
                    "receive_message",
                    {
                        "system": True,
                        "message": f"{username} left the room.",
                        "timestamp": datetime.now().strftime("%H:%M"),
                    },
                    to=room_name,
                )
                emit(
                    "online_count",
                    {"count": len(bucket["usernames"])},
                    to=room_name,
                )
        print(f"[socket] {username} disconnected.")

    @socketio.on("join")
    def handle_join(data):
        """
        A user joins a chat room.
        Steps:
            1. Add their socket to the Socket.IO room.
            2. Track them in our in-memory room bucket (for online counts).
            3. Load message history from the database and send it privately.
            4. Broadcast a "X joined the room" system message to everyone else.
        """
        room_name = data.get("room")
        username = session.get("username")
        if not room_name or not username:
            return

        join_room(room_name)
        bucket = _get_room_bucket(room_name)
        bucket["usernames"].add(username)

        # --- Load and send previous message history to the joining user only ---
        room = Room.query.filter_by(room_name=room_name).first()
        history = []
        if room:
            past_messages = (
                Message.query.filter_by(room_id=room.id)
                .order_by(Message.timestamp.asc())
                .all()
            )
            history = [m.to_dict() for m in past_messages]

        emit("message_history", {"history": history})

        # --- Notify everyone in the room (including the joiner) ---
        emit(
            "receive_message",
            {
                "system": True,
                "message": f"{username} joined the room.",
                "timestamp": datetime.now().strftime("%H:%M"),
            },
            to=room_name,
        )

        emit("online_count", {"count": len(bucket["usernames"])}, to=room_name)

    @socketio.on("leave")
    def handle_leave(data):
        """A user explicitly leaves a chat room (e.g. clicked 'Leave Room')."""
        room_name = data.get("room")
        username = session.get("username")
        if not room_name or not username:
            return

        leave_room(room_name)
        bucket = _get_room_bucket(room_name)
        bucket["usernames"].discard(username)

        emit(
            "receive_message",
            {
                "system": True,
                "message": f"{username} left the room.",
                "timestamp": datetime.now().strftime("%H:%M"),
            },
            to=room_name,
        )
        emit("online_count", {"count": len(bucket["usernames"])}, to=room_name)

    @socketio.on("send_message")
    def handle_send_message(data):
        """
        A user sends a chat message.
        Steps:
            1. Convert any emoji shortcodes (:smile: -> unicode).
            2. Persist the message to SQLite.
            3. Broadcast it to everyone currently in the room.
        """
        room_name = data.get("room")
        raw_text = (data.get("message") or "").strip()
        username = session.get("username")

        if not room_name or not raw_text or not username:
            return

        # Convert emoji shortcodes before storing/broadcasting
        processed_text = convert_emoji_shortcodes(raw_text)

        # Persist to the database
        room = Room.query.filter_by(room_name=room_name).first()
        user = User.query.filter_by(username=username).first()

        if room and user:
            new_message = Message(
                room_id=room.id,
                user_id=user.id,
                message=processed_text,
                timestamp=datetime.now(),
            )
            db.session.add(new_message)
            db.session.commit()
            payload = new_message.to_dict()
        else:
            # Fallback (should not normally happen) so the message still shows live
            payload = {
                "username": username,
                "message": processed_text,
                "timestamp": datetime.now().strftime("%H:%M"),
            }

        emit("receive_message", payload, to=room_name)

    @socketio.on("typing")
    def handle_typing(data):
        """Broadcast to the room (except sender) that this user is typing."""
        room_name = data.get("room")
        username = session.get("username")
        if not room_name or not username:
            return
        emit("typing", {"username": username}, to=room_name, include_self=False)

    @socketio.on("stop_typing")
    def handle_stop_typing(data):
        """Broadcast to the room (except sender) that this user stopped typing."""
        room_name = data.get("room")
        username = session.get("username")
        if not room_name or not username:
            return
        emit("stop_typing", {"username": username}, to=room_name, include_self=False)
