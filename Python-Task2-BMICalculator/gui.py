"""Tkinter user interface for the BMI Calculator."""

import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from bmi import BMIResult, BMICalculator
from charts import GraphManager
from database import DatabaseManager
from utils import current_timestamp, parse_positive_number, validate_name


class BMIApp:
    """Main application window and event coordinator."""

    def __init__(self, root: tk.Tk, database_path: str | Path = "bmi_database.db") -> None:
        self.root = root
        self.root.title("BMI Calculator")
        self.root.geometry("720x650")
        self.root.minsize(720, 650)
        self.root.maxsize(720, 650)
        self._center_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.calculator = BMICalculator()
        self.graph_manager = GraphManager()
        self.database = DatabaseManager(database_path)
        self.current_result: BMIResult | None = None
        self.current_inputs: tuple[str, float, float] | None = None

        try:
            self.database.initialize()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not initialize the database.\n\n{error}", parent=root)
            raise

        self._create_variables()
        self._configure_style()
        self._build_interface()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 720, 650
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_variables(self) -> None:
        self.username_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.bmi_var = tk.StringVar(value="—")
        self.category_var = tk.StringVar(value="Enter your details to calculate BMI")
        self.message_var = tk.StringVar(value="Your result and health guidance will appear here.")

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("App.TFrame", background="#f4f7fb")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("Title.TLabel", background="#f4f7fb", foreground="#16324f", font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#f4f7fb", foreground="#607d8b", font=("Segoe UI", 10))
        style.configure("Field.TLabel", background="#ffffff", foreground="#263238", font=("Segoe UI", 10, "bold"))
        style.configure("Result.TLabel", background="#ffffff", foreground="#263238", font=("Segoe UI", 11))
        style.configure("BMI.TLabel", background="#ffffff", foreground="#1976d2", font=("Segoe UI", 38, "bold"))
        style.configure("Message.TLabel", background="#ffffff", foreground="#546e7a", font=("Segoe UI", 10), wraplength=560)
        style.configure("Primary.TButton", background="#1976d2", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.map("Primary.TButton", background=[("active", "#125ca5")], foreground=[("active", "#ffffff")])
        style.configure("PrimaryHover.TButton", background="#125ca5", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Secondary.TButton", background="#e6eef7", foreground="#16324f", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.map("Secondary.TButton", background=[("active", "#cbdced")])
        style.configure("SecondaryHover.TButton", background="#cbdced", foreground="#16324f", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Danger.TButton", background="#ffebee", foreground="#b71c1c", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.map("Danger.TButton", background=[("active", "#ffcdd2")])
        style.configure("Focus.TEntry", bordercolor="#1976d2", lightcolor="#1976d2", darkcolor="#1976d2", padding=8)
        style.configure("TEntry", padding=8, fieldbackground="#ffffff")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build_interface(self) -> None:
        main_frame = ttk.Frame(self.root, style="App.TFrame", padding=26)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="BMI Calculator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(main_frame, text="Track your body mass index and understand your trend over time.", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 20))

        input_card = ttk.Frame(main_frame, style="Card.TFrame", padding=22)
        input_card.pack(fill="x")
        input_card.columnconfigure(1, weight=1)
        self._add_field(input_card, 0, "User name", self.username_var, "e.g. Alex Johnson")
        self._add_field(input_card, 1, "Weight (kg)", self.weight_var, "e.g. 68.5")
        self._add_field(input_card, 2, "Height (meters)", self.height_var, "e.g. 1.72")

        button_frame = ttk.Frame(input_card, style="Card.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        for column in range(4):
            button_frame.columnconfigure(column, weight=1)
        self._add_button(button_frame, "Calculate BMI", self.calculate_bmi, "Primary.TButton", 0)
        self._add_button(button_frame, "Save Record", self.save_record, "Secondary.TButton", 1)
        self._add_button(button_frame, "Clear", self.clear_fields, "Secondary.TButton", 2)
        self._add_button(button_frame, "Exit", self.on_exit, "Danger.TButton", 3)

        result_card = ttk.Frame(main_frame, style="Card.TFrame", padding=22)
        result_card.pack(fill="both", expand=True, pady=(18, 0))
        ttk.Label(result_card, text="YOUR RESULT", style="Field.TLabel").pack(anchor="w")
        ttk.Label(result_card, textvariable=self.bmi_var, style="BMI.TLabel").pack(anchor="w", pady=(6, 0))
        self.category_label = ttk.Label(result_card, textvariable=self.category_var, style="Result.TLabel")
        self.category_label.pack(anchor="w", pady=(0, 12))
        ttk.Separator(result_card, orient="horizontal").pack(fill="x", pady=(0, 14))
        ttk.Label(result_card, textvariable=self.message_var, style="Message.TLabel").pack(anchor="w")

        result_actions = ttk.Frame(result_card, style="Card.TFrame")
        result_actions.pack(fill="x", side="bottom", pady=(22, 0))
        self._add_button(result_actions, "Show History", self.show_history, "Secondary.TButton", 0)
        self._add_button(result_actions, "Show BMI Trend Graph", self.show_trend, "Primary.TButton", 1)
        result_actions.columnconfigure(0, weight=1)
        result_actions.columnconfigure(1, weight=1)

        self.root.bind("<Return>", lambda _event: self.calculate_bmi())

    @staticmethod
    def _add_field(parent: ttk.Frame, row: int, label: str, variable: tk.StringVar, hint: str) -> None:
        ttk.Label(parent, text=label, style="Field.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 18), pady=7)
        entry = ttk.Entry(parent, textvariable=variable, font=("Segoe UI", 10))
        entry.grid(row=row, column=1, sticky="ew", pady=7)
        entry.insert(0, "")
        entry.configure(cursor="xterm")
        entry.bind("<FocusIn>", lambda event: event.widget.configure(style="Focus.TEntry"))
        entry.bind("<FocusOut>", lambda event: event.widget.configure(style="TEntry"))
        ttk.Label(parent, text=hint, style="Subtitle.TLabel").grid(row=row, column=2, sticky="w", padx=(12, 0), pady=7)

    @staticmethod
    def _add_button(parent: ttk.Frame, text: str, command: Any, style: str, column: int) -> None:
        button = ttk.Button(parent, text=text, command=command, style=style)
        button.grid(row=0, column=column, sticky="ew", padx=4)
        hover_style = "PrimaryHover.TButton" if style == "Primary.TButton" else "SecondaryHover.TButton"
        button.bind("<Enter>", lambda _event: button.configure(style=hover_style))
        button.bind("<Leave>", lambda _event: button.configure(style=style))

    def _get_validated_inputs(self) -> tuple[str, float, float]:
        username = validate_name(self.username_var.get())
        weight = parse_positive_number(self.weight_var.get(), "Weight", 500)
        height = parse_positive_number(self.height_var.get(), "Height", 3)
        return username, weight, height

    def calculate_bmi(self) -> None:
        """Validate inputs and show the calculated BMI."""
        try:
            username, weight, height = self._get_validated_inputs()
            self.current_result = self.calculator.calculate(weight, height)
            self.current_inputs = (username, weight, height)
            self.bmi_var.set(f"{self.current_result.bmi:.2f}")
            self.category_var.set(self.current_result.category)
            self.message_var.set(self.current_result.health_message)
            self.category_label.configure(foreground=BMICalculator.color_for(self.current_result.category))
        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error), parent=self.root)
        except Exception as error:  # Defensive UI boundary for unexpected errors.
            messagebox.showerror("Calculation Error", f"Unable to calculate BMI.\n\n{error}", parent=self.root)

    def save_record(self) -> None:
        """Save the latest calculation, recalculating when needed."""
        try:
            inputs = self._get_validated_inputs()
            if self.current_result is None or self.current_inputs != inputs:
                self.calculate_bmi()
                if self.current_result is None:
                    return
                inputs = self.current_inputs
            assert inputs is not None and self.current_result is not None
            username, weight, height = inputs
            self.database.save_record(
                username,
                weight,
                height,
                self.current_result.bmi,
                self.current_result.category,
                current_timestamp(),
            )
            messagebox.showinfo("Record Saved", f"BMI record saved for {username}.", parent=self.root)
        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error), parent=self.root)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not save the record.\n\n{error}", parent=self.root)
        except Exception as error:
            messagebox.showerror("Save Error", f"Unable to save the record.\n\n{error}", parent=self.root)

    def show_history(self) -> None:
        """Open a sortable-looking read-only history table for the selected user."""
        try:
            username = validate_name(self.username_var.get())
            records = self.database.get_records(username)
            if not records:
                messagebox.showinfo("No Records", f"No BMI records found for {username}.", parent=self.root)
                return

            history_window = tk.Toplevel(self.root)
            history_window.title(f"BMI History — {username}")
            history_window.geometry("760x420")
            history_window.minsize(650, 320)
            history_window.transient(self.root)
            frame = ttk.Frame(history_window, padding=16)
            frame.pack(fill="both", expand=True)
            ttk.Label(frame, text=f"BMI history for {username}", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 12))

            table_frame = ttk.Frame(frame)
            table_frame.pack(fill="both", expand=True)
            columns = ("date", "weight", "height", "bmi", "category")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings")
            headings = {"date": "Date", "weight": "Weight (kg)", "height": "Height (m)", "bmi": "BMI", "category": "Category"}
            widths = {"date": 170, "weight": 100, "height": 100, "bmi": 85, "category": 150}
            for column in columns:
                tree.heading(column, text=headings[column])
                tree.column(column, width=widths[column], anchor="center")
            for record in records:
                tree.insert("", "end", values=(record["date"], f"{record['weight']:.2f}", f"{record['height']:.2f}", f"{record['bmi']:.2f}", record["category"]))
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error), parent=self.root)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not load history.\n\n{error}", parent=self.root)
        except Exception as error:
            messagebox.showerror("History Error", f"Unable to load history.\n\n{error}", parent=self.root)

    def show_trend(self) -> None:
        """Display a BMI trend for the selected user or all users."""
        try:
            raw_username = self.username_var.get().strip()
            username = validate_name(raw_username) if raw_username else None
            records = self.database.get_records(username)
            title = f"BMI Trend — {username}" if username else "BMI Trend — All Users"
            self.graph_manager.show_trend(self.root, records, title)
        except ValueError as error:
            messagebox.showinfo("No Records", str(error), parent=self.root)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not load BMI trend data.\n\n{error}", parent=self.root)
        except (RuntimeError, OSError) as error:
            messagebox.showerror("Graph Error", str(error), parent=self.root)
        except Exception as error:
            messagebox.showerror("Graph Error", f"Unable to display the BMI trend.\n\n{error}", parent=self.root)

    def clear_fields(self) -> None:
        """Clear form inputs and reset the displayed calculation."""
        self.username_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.current_result = None
        self.current_inputs = None
        self.bmi_var.set("—")
        self.category_var.set("Enter your details to calculate BMI")
        self.message_var.set("Your result and health guidance will appear here.")
        self.category_label.configure(foreground="#263238")

    def on_exit(self) -> None:
        """Close the database and application safely."""
        try:
            self.database.close()
        finally:
            self.root.destroy()


def launch_app(database_path: str | Path = "bmi_database.db") -> None:
    """Launch the BMI Calculator application."""
    root = tk.Tk()
    try:
        BMIApp(root, database_path)
        root.mainloop()
    except Exception:
        # Initialization errors have already been reported to the user where possible.
        # Ensure the process exits cleanly instead of leaving a hidden Tk root alive.
        if root.winfo_exists():
            root.destroy()
