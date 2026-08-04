# 💬 Real-Time Chat Application

A full-stack, real-time chat application built with **Flask**, **Flask-SocketIO**, **SQLAlchemy**, and **Bootstrap 5**. Users can register, log in, create or join chat rooms, and exchange messages instantly — with typing indicators, emoji shortcodes, browser notifications, and persistent message history.

---

## ✨ Features

- **User Registration & Login** — hashed passwords, duplicate-username prevention, Flask session-based auth
- **Protected Routes** — dashboard and chat rooms require login
- **Dashboard** — welcome banner, list of available rooms, create/join room forms
- **Chat Rooms** — create, join, and leave rooms (unique room names)
- **Real-Time Messaging** — powered by Flask-SocketIO, instant delivery with no page refresh
- **Message History** — every message is stored in SQLite and reloaded when a user joins a room
- **Typing Indicators** — "Alice is typing..." shown live, auto-clears when typing stops
- **Join/Leave Notifications** — system messages announce when users enter or leave a room
- **Browser Notifications** — desktop notification shown when a new message arrives while the tab is inactive (permission requested automatically)
- **Emoji Shortcodes** — `:smile:` `:heart:` `:laugh:` `:sad:` `:fire:` `:thumbsup:` `:rocket:` converted to Unicode emoji
- **Modern, Responsive UI** — Bootstrap 5, gradient accents, rounded chat bubbles, sidebar, dark mode toggle, auto-scroll, online user count
- **Security** — password hashing (Werkzeug/PBKDF2), SQLAlchemy ORM (prevents SQL injection), HTML-escaped message rendering (via `textContent`), input validation

---

## 📸 Screenshots

> _Add screenshots here after running the app locally._

- `Login Page` — ![login screenshot placeholder](static/images/screenshot-login.png)
- `Dashboard` — ![dashboard screenshot placeholder](static/images/screenshot-dashboard.png)
- `Chat Room` — ![chat room screenshot placeholder](static/images/screenshot-room.png)

---

## 📁 Folder Structure

```
ChatApp/
│
├── app.py                 # Main Flask app: routes + app/SocketIO setup
├── config.py               # App configuration (secret key, DB URI, etc.)
├── models.py                # SQLAlchemy models: User, Room, Message
├── socket_events.py          # All Flask-SocketIO event handlers
├── requirements.txt           # Python dependencies
├── README.md                   # This file
├── database.db                  # SQLite database (auto-created on first run)
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styling on top of Bootstrap 5
│   ├── js/
│   │   └── chat.js         # Client-side Socket.IO logic
│   └── images/              # Static image assets (icons, screenshots)
│
├── templates/
│   ├── layout.html          # Shared base template (navbar, flash messages, dark mode)
│   ├── login.html            # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html          # Post-login dashboard (rooms list, create/join)
│   └── room.html                # Live chat room page
│
└── utils/
    ├── auth.py               # Password hashing/verification, login_required decorator
    └── emoji.py               # Emoji shortcode -> Unicode conversion
```

---

## ⚙️ Requirements

- Python 3.9+
- pip

All Python dependencies are listed in `requirements.txt`:

```
Flask
Flask-SocketIO
Flask-SQLAlchemy
python-socketio
python-engineio
Werkzeug
python-dotenv
eventlet
```

---

## 🚀 Installation

1. **Clone or download this project**, then move into the project folder:
   ```bash
   cd ChatApp
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - macOS / Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ How to Run

```bash
python app.py
```

The app will:
- Automatically create `database.db` and all tables on first run.
- Start the Flask-SocketIO development server at **http://localhost:5000**.

Open the URL in **multiple browser tabs or windows** to simulate multiple users chatting in real time.

---

## 🔐 Security Transparency

This project follows good baseline security practices, but is intended as a **learning / demo project**, not a production-hardened system. Please note:

- **Password Storage:** Passwords are never stored in plain text — they are hashed using Werkzeug's secure `generate_password_hash` (PBKDF2 with salt).
- **Database:** All application data (users, rooms, messages) is stored in a local **SQLite** database (`database.db`) accessed through SQLAlchemy, which parameterizes queries and prevents SQL injection.
- **Real-Time Communication:** Messages are transmitted using **Socket.IO** over the app's existing HTTP(S) connection.
- **No End-to-End Encryption:** Messages are **NOT end-to-end encrypted**. They are readable by the server and stored in plain text in the database. Do not use this app for sensitive or confidential communication without adding encryption.
- **Session Security:** Sessions use Flask's signed session cookies (`SECRET_KEY`); change the default secret key before any real-world deployment.
- **Input Handling:** Server-side validation is applied to registration input; message content is rendered client-side via `textContent` (not `innerHTML`) to avoid HTML/script injection.

---

## 🌱 Future Improvements

- End-to-end message encryption
- Private (1-on-1) direct messaging
- File / image sharing in chat
- Message editing & deletion
- Persistent dark mode preference (e.g., per-user setting stored in the database)
- Read receipts
- Admin/moderation tools (kick/ban, room ownership)
- Pagination / infinite scroll for very long message histories
- Deployment guide for production (Gunicorn + eventlet/gevent workers, Nginx reverse proxy, HTTPS)
- Rate limiting to prevent message spam

---

## 🧩 Socket.IO Events Reference

| Event            | Direction        | Purpose                                      |
|-------------------|-----------------|-----------------------------------------------|
| `connect`         | client → server | Fired when a socket connects                  |
| `disconnect`      | client → server | Fired when a socket disconnects               |
| `join`            | client → server | Join a room, load history, notify others      |
| `leave`           | client → server | Leave a room, notify others                   |
| `send_message`    | client → server | Send a new chat message                       |
| `receive_message` | server → client | Deliver a chat message or system notice       |
| `message_history` | server → client | Deliver stored history on join                |
| `typing`          | client → server | Notify others "user is typing"                |
| `stop_typing`     | client → server | Notify others typing has stopped              |
| `online_count`    | server → client | Update the online user count in a room        |

---

Built with ❤️ using Flask, Flask-SocketIO, SQLAlchemy, and Bootstrap 5.
