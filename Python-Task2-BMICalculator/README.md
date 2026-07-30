# BMI Calculator Desktop and Streamlit Application

A production-ready Body Mass Index calculator built with Python, Tkinter, SQLite, Matplotlib, and Streamlit. It provides both a desktop GUI and a browser-based interface for calculating BMI, saving named user records, reviewing history, and visualizing progress over time.

## Features

- Modern `ttk` interface with a centered fixed-size window
- User name, weight, and height input with friendly validation errors
- BMI calculation rounded to two decimal places
- Underweight, Normal Weight, Overweight, and Obese classification
- Category colors: blue, green, orange, and red
- Hover states for the main action buttons
- SQLite database created automatically on first run
- Parameterized record inserts and a user/date query index
- BMI history window with a scrollable `ttk.Treeview`
- Matplotlib trend graph with dates, markers, grid, legend, and axis labels
- Idempotent sample data for `Sample User` on a brand-new database
- Defensive handling for input, SQLite, chart, and unexpected UI errors
- Streamlit browser interface with responsive layout, result cards, history table, and trend chart

## Technologies

- Python 3.12+
- Tkinter and `ttk`
- SQLite3 (Python standard library)
- Matplotlib
- Object-oriented Python design

## Installation

1. Install Python 3.12 or newer.
2. Open a terminal in this project directory.
3. Optionally create a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the required library:

   ```bash
   python -m pip install -r requirements.txt
   ```

Tkinter is usually included with standard Python installations. On some Linux distributions, install the system package named `python3-tk`.

## How to run

### Desktop application

```bash
python main.py
```

### Streamlit application

```bash
streamlit run streamlit_app.py
```

Streamlit will open the application in your browser. The desktop and Streamlit interfaces use the same `bmi_database.db` file.

The application creates `bmi_database.db` in the project directory automatically. A fresh database is populated with three `Sample User` records so the history and trend views can be tried immediately. New databases are never reseeded after a user record exists.

## Project structure

```text
.
├── bmi.py             # BMI calculation and classification
├── charts.py          # Matplotlib trend graph
├── database.py        # SQLite schema and persistence
├── gui.py             # Tkinter application UI
├── main.py            # Entry point
├── requirements.txt   # Third-party dependencies
├── streamlit_app.py   # Streamlit browser interface
├── utils.py           # Input and timestamp helpers
└── bmi_database.db    # Created automatically on first run
```

## Future improvements

- Add edit/delete controls with an explicit confirmation step
- Add user selection and profile management
- Export history to CSV or PDF
- Add optional age, sex, and unit conversion support
- Add automated UI tests and packaging for Windows/macOS/Linux

## Health note

BMI is a screening measure, not a diagnosis. The health messages in this app are general guidance and should not replace advice from a qualified healthcare professional.
