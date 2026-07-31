/* ==========================================================
   chat.js — Client-side real-time chat logic (Socket.IO)
   Handles: join/leave, sending/receiving messages, message
   history, typing indicators, online counts, browser
   notifications, and auto-scroll.
   ========================================================== */

(function () {
    "use strict";

    // Elements
    const messagesEl = document.getElementById("messages");
    const messageForm = document.getElementById("messageForm");
    const messageInput = document.getElementById("messageInput");
    const typingIndicatorEl = document.getElementById("typingIndicator");
    const onlineCountEl = document.getElementById("onlineCount");
    const leaveRoomBtn = document.getElementById("leaveRoomBtn");

    // Connect to the Socket.IO server
    const socket = io();

    // Typing state
    let typingTimeout = null;
    const typingUsers = new Set();

    // Track whether this tab is currently visible (for notifications)
    let tabIsActive = true;
    document.addEventListener("visibilitychange", () => {
        tabIsActive = document.visibilityState === "visible";
        if (tabIsActive) {
            document.title = "ChatApp";
        }
    });

    // ---------------------------------------------------------
    // Browser Notification permission (requested automatically)
    // ---------------------------------------------------------
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }

    function notifyNewMessage(username, text) {
        if (tabIsActive) return; // Only notify when tab is inactive
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification(`New message from ${username}`, {
                body: text,
                icon: "/static/images/chat-icon.png",
            });
        }
        // Flash the tab title too, as a lightweight fallback indicator
        document.title = `💬 New message — ChatApp`;
    }

    // ---------------------------------------------------------
    // Helpers to render messages into the DOM
    // ---------------------------------------------------------
    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function appendSystemMessage(text) {
        const div = document.createElement("div");
        div.className = "system-message";
        div.textContent = text;
        messagesEl.appendChild(div);
        scrollToBottom();
    }

    function appendChatMessage({ username, message, timestamp }) {
        const isMine = username === CURRENT_USERNAME;

        const row = document.createElement("div");
        row.className = `message-row ${isMine ? "mine" : "theirs"}`;

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.textContent = message; // textContent -> safe from HTML injection (escaped)

        const meta = document.createElement("div");
        meta.className = "msg-meta";
        meta.textContent = `${isMine ? "You" : username} · ${timestamp}`;

        row.appendChild(bubble);
        row.appendChild(meta);
        messagesEl.appendChild(row);
        scrollToBottom();
    }

    // ---------------------------------------------------------
    // Join the room as soon as the page loads
    // ---------------------------------------------------------
    socket.on("connect", () => {
        socket.emit("join", { room: CURRENT_ROOM });
    });

    // Load message history (sent once, right after joining)
    socket.on("message_history", (data) => {
        messagesEl.innerHTML = "";
        (data.history || []).forEach((msg) => appendChatMessage(msg));
    });

    // Receive a new message (chat message OR system join/leave message)
    socket.on("receive_message", (data) => {
        if (data.system) {
            appendSystemMessage(data.message);
        } else {
            appendChatMessage(data);
            if (data.username !== CURRENT_USERNAME) {
                notifyNewMessage(data.username, data.message);
            }
        }
    });

    // Online user count updates
    socket.on("online_count", (data) => {
        onlineCountEl.textContent = data.count;
    });

    // ---------------------------------------------------------
    // Typing indicator
    // ---------------------------------------------------------
    socket.on("typing", (data) => {
        typingUsers.add(data.username);
        renderTypingIndicator();
    });

    socket.on("stop_typing", (data) => {
        typingUsers.delete(data.username);
        renderTypingIndicator();
    });

    function renderTypingIndicator() {
        if (typingUsers.size === 0) {
            typingIndicatorEl.textContent = "";
            return;
        }
        const names = Array.from(typingUsers);
        const verb = names.length === 1 ? "is" : "are";
        typingIndicatorEl.textContent = `${names.join(", ")} ${verb} typing...`;
    }

    // ---------------------------------------------------------
    // Sending messages
    // ---------------------------------------------------------
    messageForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (!text) return;

        socket.emit("send_message", { room: CURRENT_ROOM, message: text });
        socket.emit("stop_typing", { room: CURRENT_ROOM });
        clearTimeout(typingTimeout);

        messageInput.value = "";
        messageInput.focus();
    });

    // Press Enter to send (default form submit already covers this,
    // but we guard against Shift+Enter in case of future multi-line support)
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            // Let the form's submit handler take care of sending.
            // (No preventDefault needed since input is single-line.)
        }
    });

    // Emit typing / stop_typing events as the user types
    messageInput.addEventListener("input", () => {
        socket.emit("typing", { room: CURRENT_ROOM });

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socket.emit("stop_typing", { room: CURRENT_ROOM });
        }, 1200);
    });

    // ---------------------------------------------------------
    // Leaving the room via the sidebar button
    // ---------------------------------------------------------
    if (leaveRoomBtn) {
        leaveRoomBtn.addEventListener("click", () => {
            socket.emit("leave", { room: CURRENT_ROOM });
            // Navigation to /dashboard proceeds normally via the <a href>
        });
    }

    // Also notify the server if the user closes/refreshes the tab
    window.addEventListener("beforeunload", () => {
        socket.emit("leave", { room: CURRENT_ROOM });
    });
})();
