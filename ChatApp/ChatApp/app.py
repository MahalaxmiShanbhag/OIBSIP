"""
app.py
------
Main entry point for the Real-Time Chat Application.

Responsibilities:
    - Create and configure the Flask app
    - Initialize the database (SQLAlchemy)
    - Initialize Flask-SocketIO
    - Define HTTP routes (register / login / logout / dashboard / room)
    - Register Socket.IO event handlers (see socket_events.py)

Run with:
    python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO

from config import Config
from models import db, User, Room
from utils.auth import hash_password, verify_password, login_required, validate_registration_input
from socket_events import register_socket_events


def create_app():
    """Application factory: builds and configures the Flask app instance."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    return app


# --- Create the app and SocketIO instance at module level so `flask run`
#     and `python app.py` both work, and so socket_events can be registered. ---
app = create_app()
socketio = SocketIO(app, async_mode=Config.SOCKETIO_ASYNC_MODE, cors_allowed_origins="*")
register_socket_events(socketio)


# =========================================================
#                      HTTP ROUTES
# =========================================================

@app.route("/")
def index():
    """Redirect root URL to dashboard (if logged in) or login page."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle new user registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = validate_registration_input(username, password, confirm_password)

        # Prevent duplicate usernames
        if not errors and User.query.filter_by(username=username).first():
            errors.append("That username is already taken.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("register.html")

        new_user = User(username=username, password=hash_password(password))
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login using Flask session-based authentication."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and verify_password(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear the session and log the user out."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """
    Show the dashboard: welcome message, list of rooms, and forms to
    create or join a room.
    """
    if request.method == "POST":
        action = request.form.get("action")
        room_name = request.form.get("room_name", "").strip()

        if not room_name:
            flash("Room name cannot be empty.", "danger")
            return redirect(url_for("dashboard"))

        if action == "create":
            if Room.query.filter_by(room_name=room_name).first():
                flash("A room with that name already exists.", "danger")
            else:
                new_room = Room(room_name=room_name)
                db.session.add(new_room)
                db.session.commit()
                flash(f"Room '{room_name}' created!", "success")
                return redirect(url_for("room", room_name=room_name))

        elif action == "join":
            room = Room.query.filter_by(room_name=room_name).first()
            if not room:
                flash("That room does not exist.", "danger")
            else:
                return redirect(url_for("room", room_name=room_name))

        return redirect(url_for("dashboard"))

    rooms = Room.query.order_by(Room.created_at.desc()).all()
    return render_template("dashboard.html", username=session.get("username"), rooms=rooms)


@app.route("/room/<room_name>")
@login_required
def room(room_name):
    """Render the chat room page. Real-time behavior is handled by chat.js + Socket.IO."""
    room_obj = Room.query.filter_by(room_name=room_name).first()
    if not room_obj:
        flash("That room does not exist.", "danger")
        return redirect(url_for("dashboard"))

    return render_template(
        "room.html", username=session.get("username"), room_name=room_name
    )


# =========================================================
#                      APP STARTUP
# =========================================================

def init_db():
    """Create all database tables if they do not already exist."""
    with app.app_context():
        db.create_all()


init_db()

if __name__ == "__main__":
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=5000,
        allow_unsafe_werkzeug=True
    )