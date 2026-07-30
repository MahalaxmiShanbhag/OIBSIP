# 🔐 Advanced Password Generator

A modern, secure, and fully-featured desktop **Password Generator** built with Python and Tkinter. It uses Python's cryptographically secure `secrets` module (never `random`) to generate strong, customizable passwords through a clean, professional GUI.

---

## 📋 Project Overview

This application lets users generate strong, random passwords tailored to their exact requirements — length, character composition, and readability — while guaranteeing cryptographic security. It's designed to be beginner-friendly to run, yet built with production-quality modular architecture, type hints, and proper exception handling.

---

## ✨ Features

- **Adjustable Password Length** — Choose any length from **8 to 64** characters using a slider or a precise Spinbox (default: 16).
- **Character Type Selection** — Toggle Uppercase, Lowercase, Numbers, and Symbols independently. At least **two** types must be selected.
- **Exclude Ambiguous Characters** — Optionally strip visually confusing characters (`0`, `O`, `o`, `1`, `l`, `I`) from generated passwords.
- **Cryptographically Secure Generation** — Powered entirely by the `secrets` module, including a secure Fisher–Yates shuffle. **The `random` module is never used.**
- **Guaranteed Character Diversity** — Every generated password contains at least one character from each selected category.
- **Read-Only Password Display** — The generated password appears in a locked `Entry` field to prevent accidental edits.
- **One-Click Clipboard Copy** — Passwords are copied to the clipboard automatically on generation, plus a manual "Copy Password" button using `pyperclip`.
- **Live Strength Indicator** — A color-coded label (🔴 Weak / 🟠 Medium / 🟢 Strong) evaluates strength using length and character diversity.
- **Session Password History** — View your last 5 generated passwords (in-memory only — nothing is written to disk).
- **Robust Input Validation** — Friendly error dialogs for invalid lengths, insufficient character type selections, or unusable configurations.
- **Modern Dark-Themed UI** — Built with `ttk` widgets and a custom-styled dark theme for a polished, professional look.

---

## 🛠 Technologies Used

| Technology  | Purpose                                       |
|-------------|------------------------------------------------|
| Python 3.12+ | Core programming language                     |
| `tkinter` / `ttk` | Graphical user interface                 |
| `secrets`   | Cryptographically secure random generation     |
| `string`    | Character set definitions                      |
| `collections.deque` | Efficient fixed-size session history    |
| `pyperclip` | Clipboard integration                          |

---

## 📁 Project Structure

```
PasswordGenerator/
│── main.py                 # Application entry point & Tkinter GUI
│── password_generator.py   # Core secure password generation logic
│── strength_checker.py     # Password strength evaluation logic
│── clipboard.py             # Clipboard helper (pyperclip wrapper)
│── history.py               # Session-only password history tracker
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
```

---

## ⚙️ Installation Steps

1. **Clone or download** this project folder to your local machine.

2. **Ensure Python 3.12+ is installed:**
   ```bash
   python --version
   ```

3. **(Recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   > **Note (Linux only):** `pyperclip` requires a clipboard utility such as `xclip` or `xsel` to be installed on your system:
   > ```bash
   > sudo apt-get install xclip
   > ```

---

## 📦 Required Libraries

- `pyperclip` (third-party — listed in `requirements.txt`)
- `tkinter`, `secrets`, `string`, `collections` (all part of the Python standard library — no installation needed)

---

## ▶️ How to Run

From the project root directory, run:

```bash
python main.py
```

The application window will open immediately — no additional configuration required.

---



## 🚀 Future Improvements

- Add a "Copied!" inline animation/tooltip instead of a popup dialog.
- Add an option to save favorite passwords using OS-level encrypted storage.
- Support passphrase-style generation (e.g., word-based passwords).
- Add a dark/light theme toggle.
- Add unit tests using `pytest` for full CI coverage.
- Package the app as a standalone executable using `PyInstaller`.

---

## 🔒 Security Notes

- This application uses only the `secrets` module for all randomness-related operations — it **never** uses the `random` module, making it suitable for generating security-sensitive passwords.
- Password history is kept **in memory only** for the current session and is never written to disk or transmitted anywhere.

---

## 📄 License

This project is free to use and modify for personal or educational purposes.
