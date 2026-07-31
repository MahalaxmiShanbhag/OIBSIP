"""
models.py
---------
SQLAlchemy database models for the Chat Application.

Three tables are defined:
    - User:    registered users (hashed passwords only)
    - Room:    chat rooms, each with a unique name
    - Message: chat history, linked to a Room and a User
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance, initialized in app.py via db.init_app(app)
db = SQLAlchemy()


class User(db.Model):
    """Represents a registered user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # stores the HASHED password

    # One user can author many messages
    messages = db.relationship("Message", backref="author", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Room(db.Model):
    """Represents a chat room. Room names must be unique."""

    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One room can contain many messages
    messages = db.relationship(
        "Message", backref="room", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Room {self.room_name}>"


class Message(db.Model):
    """Represents a single chat message stored for history/persistence."""

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Serialize this message for sending over Socket.IO / JSON APIs."""
        return {
            "username": self.author.username,
            "message": self.message,
            "timestamp": self.timestamp.strftime("%H:%M"),
        }

    def __repr__(self):
        return f"<Message {self.id} in Room {self.room_id}>"
