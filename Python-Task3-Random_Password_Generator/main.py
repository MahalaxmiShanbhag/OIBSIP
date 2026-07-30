"""
main.py

Advanced Password Generator — Main Application Entry Point.

A modern, secure Tkinter GUI application for generating strong
passwords. Built using:
    - tkinter / ttk for the GUI
    - secrets module for cryptographically secure randomness
    - pyperclip for clipboard integration

Run with:
    python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from password_generator import PasswordGenerator, PasswordGeneratorError
from strength_checker import StrengthChecker
from clipboard import copy_to_clipboard, ClipboardError
from history import PasswordHistory


class PasswordGeneratorApp:
    """Main application class wrapping the Tkinter GUI and its logic."""

    WINDOW_WIDTH = 560
    WINDOW_HEIGHT = 720

    # Color palette for a clean, modern look.
    BG_COLOR = "#1e1e2f"
    PANEL_COLOR = "#27293d"
    ACCENT_COLOR = "#5865f2"
    TEXT_COLOR = "#e6e6f0"
    MUTED_TEXT_COLOR = "#9a9ab0"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.history_manager = PasswordHistory(max_size=5)

        self._configure_window()
        self._configure_styles()

        # Tkinter variables bound to GUI widgets.
        self.length_var = tk.IntVar(value=PasswordGenerator.MIN_LENGTH + 8)  # default 16
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.exclude_ambiguous_var = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar(value="")
        self.strength_label_var = tk.StringVar(value="Strength: N/A")

        self._build_ui()

    # ------------------------------------------------------------------
    # Window & Style Setup
    # ------------------------------------------------------------------
    def _configure_window(self) -> None:
        """Configure the root window's title, size, and background."""
        self.root.title("Advanced Password Generator")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.root.configure(bg=self.BG_COLOR)

    def _configure_styles(self) -> None:
        """Configure ttk styles for a modern, consistent look."""
        style = ttk.Style()
        # 'clam' theme allows fuller customization than default themes.
        style.theme_use("clam")

        style.configure(
            "TFrame", background=self.BG_COLOR
        )
        style.configure(
            "Panel.TFrame", background=self.PANEL_COLOR
        )
        style.configure(
            "TLabel",
            background=self.BG_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Panel.TLabel",
            background=self.PANEL_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=self.BG_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BG_COLOR,
            foreground=self.MUTED_TEXT_COLOR,
            font=("Segoe UI", 9),
        )
        style.configure(
            "TCheckbutton",
            background=self.PANEL_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 10),
        )
        style.map(
            "TCheckbutton",
            background=[("active", self.PANEL_COLOR)],
            foreground=[("active", self.TEXT_COLOR)],
        )
        style.configure(
            "Accent.TButton",
            background=self.ACCENT_COLOR,
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padding=10,
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#4752c4")],
        )
        style.configure(
            "Secondary.TButton",
            background="#3a3d5c",
            foreground="#ffffff",
            font=("Segoe UI", 10),
            padding=8,
            borderwidth=0,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#4a4e73")],
        )
        style.configure(
            "TSpinbox",
            fieldbackground="#3a3d5c",
            background="#3a3d5c",
            foreground=self.TEXT_COLOR,
            arrowsize=14,
        )
        style.configure(
            "TEntry",
            fieldbackground="#3a3d5c",
            foreground=self.TEXT_COLOR,
            insertcolor=self.TEXT_COLOR,
        )
        style.configure(
            "Horizontal.TScale",
            background=self.PANEL_COLOR,
            troughcolor="#3a3d5c",
        )

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        """Build and lay out all widgets in the main window."""
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        self._build_header(container)
        self._build_length_section(container)
        self._build_character_options_section(container)
        self._build_action_buttons(container)
        self._build_password_display_section(container)
        self._build_strength_section(container)
        self._build_history_section(container)

    def _build_header(self, parent: ttk.Frame) -> None:
        """Build the title/header section."""
        title = ttk.Label(
            parent, text="🔐 Advanced Password Generator", style="Title.TLabel"
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            parent,
            text="Generate cryptographically secure passwords instantly.",
            style="Subtitle.TLabel",
        )
        subtitle.pack(anchor="w", pady=(2, 15))

    def _build_length_section(self, parent: ttk.Frame) -> None:
        """Build the password length selector (Spinbox + Slider)."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        panel.pack(fill="x", pady=(0, 12))

        header = ttk.Label(panel, text="Password Length", style="Panel.TLabel")
        header.grid(row=0, column=0, sticky="w", columnspan=3)

        # Slider for quick visual adjustment.
        self.length_scale = ttk.Scale(
            panel,
            from_=PasswordGenerator.MIN_LENGTH,
            to=PasswordGenerator.MAX_LENGTH,
            orient="horizontal",
            variable=self.length_var,
            command=self._on_scale_change,
        )
        self.length_scale.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Spinbox for precise numeric entry, validated on change.
        self.length_spinbox = ttk.Spinbox(
            panel,
            from_=PasswordGenerator.MIN_LENGTH,
            to=PasswordGenerator.MAX_LENGTH,
            textvariable=self.length_var,
            width=5,
            justify="center",
            command=self._on_spinbox_change,
        )
        self.length_spinbox.grid(row=1, column=2, padx=(10, 0), pady=(8, 0))
        self.length_spinbox.bind("<KeyRelease>", self._on_spinbox_change)
        self.length_spinbox.bind("<FocusOut>", self._on_spinbox_change)

        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)

    def _build_character_options_section(self, parent: ttk.Frame) -> None:
        """Build checkboxes for character type selection and exclusions."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        panel.pack(fill="x", pady=(0, 12))

        header = ttk.Label(panel, text="Character Types", style="Panel.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Checkbutton(
            panel, text="Uppercase Letters (A-Z)", variable=self.uppercase_var
        ).grid(row=1, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            panel, text="Lowercase Letters (a-z)", variable=self.lowercase_var
        ).grid(row=2, column=0, sticky="w", pady=2)

        ttk.Checkbutton(
            panel, text="Numbers (0-9)", variable=self.numbers_var
        ).grid(row=1, column=1, sticky="w", pady=2, padx=(20, 0))

        ttk.Checkbutton(
            panel, text="Symbols (!@#$...)", variable=self.symbols_var
        ).grid(row=2, column=1, sticky="w", pady=2, padx=(20, 0))

        separator = ttk.Separator(panel, orient="horizontal")
        separator.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Checkbutton(
            panel,
            text="Exclude Ambiguous Characters (0, O, o, 1, l, I)",
            variable=self.exclude_ambiguous_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w")

    def _build_action_buttons(self, parent: ttk.Frame) -> None:
        """Build the primary 'Generate Password' action button."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(0, 12))

        generate_btn = ttk.Button(
            button_frame,
            text="🔄  Generate Password",
            style="Accent.TButton",
            command=self.on_generate_click,
        )
        generate_btn.pack(fill="x")

    def _build_password_display_section(self, parent: ttk.Frame) -> None:
        """Build the read-only password display and copy button."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        panel.pack(fill="x", pady=(0, 12))

        header = ttk.Label(panel, text="Generated Password", style="Panel.TLabel")
        header.pack(anchor="w", pady=(0, 8))

        row = ttk.Frame(panel, style="Panel.TFrame")
        row.pack(fill="x")

        self.password_entry = ttk.Entry(
            row,
            textvariable=self.password_var,
            font=("Consolas", 13),
            justify="center",
            state="readonly",
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=6)

        copy_btn = ttk.Button(
            row,
            text="📋 Copy",
            style="Secondary.TButton",
            command=self.on_copy_click,
        )
        copy_btn.pack(side="left", padx=(10, 0))

    def _build_strength_section(self, parent: ttk.Frame) -> None:
        """Build the password strength indicator section."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        panel.pack(fill="x", pady=(0, 12))

        header = ttk.Label(panel, text="Password Strength", style="Panel.TLabel")
        header.pack(anchor="w", pady=(0, 8))

        self.strength_display = tk.Label(
            panel,
            textvariable=self.strength_label_var,
            font=("Segoe UI", 11, "bold"),
            bg=self.PANEL_COLOR,
            fg=self.MUTED_TEXT_COLOR,
            anchor="w",
        )
        self.strength_display.pack(fill="x")

        # A simple colored bar for a quick visual strength cue.
        self.strength_bar = tk.Frame(panel, height=8, bg="#3a3d5c")
        self.strength_bar.pack(fill="x", pady=(8, 0))

    def _build_history_section(self, parent: ttk.Frame) -> None:
        """Build the session password history list section."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        panel.pack(fill="both", expand=True)

        header = ttk.Label(
            panel, text="Password History (this session, last 5)", style="Panel.TLabel"
        )
        header.pack(anchor="w", pady=(0, 8))

        self.history_listbox = tk.Listbox(
            panel,
            bg="#3a3d5c",
            fg=self.TEXT_COLOR,
            font=("Consolas", 11),
            selectbackground=self.ACCENT_COLOR,
            highlightthickness=0,
            borderwidth=0,
            activestyle="none",
        )
        self.history_listbox.pack(fill="both", expand=True)
        # Clicking a history entry re-populates the display + clipboard.
        self.history_listbox.bind("<<ListboxSelect>>", self.on_history_select)

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _on_scale_change(self, _value: str) -> None:
        """Keep the Spinbox in sync when the slider moves (rounds to int)."""
        self.length_var.set(int(float(self.length_scale.get())))

    def _on_spinbox_change(self, _event=None) -> None:
        """Validate and sync the slider when the Spinbox value changes."""
        try:
            value = int(self.length_spinbox.get())
        except (ValueError, tk.TclError):
            return  # Ignore transient invalid states while typing.

        # Clamp to the allowed range to keep the slider consistent.
        value = max(PasswordGenerator.MIN_LENGTH, min(PasswordGenerator.MAX_LENGTH, value))
        self.length_var.set(value)

    def on_generate_click(self) -> None:
        """Handle the 'Generate Password' button click."""
        try:
            length = self._get_validated_length()
        except PasswordGeneratorError as exc:
            messagebox.showerror("Invalid Length", str(exc))
            return

        generator = PasswordGenerator(
            length=length,
            use_uppercase=self.uppercase_var.get(),
            use_lowercase=self.lowercase_var.get(),
            use_numbers=self.numbers_var.get(),
            use_symbols=self.symbols_var.get(),
            exclude_ambiguous=self.exclude_ambiguous_var.get(),
        )

        try:
            password = generator.generate()
        except PasswordGeneratorError as exc:
            messagebox.showerror("Cannot Generate Password", str(exc))
            return

        # Update the password display.
        self.password_var.set(password)

        # Update strength indicator.
        self._update_strength_indicator(password)

        # Update session history.
        self.history_manager.add(password)
        self._refresh_history_display()

        # Automatically copy to clipboard as required.
        try:
            copy_to_clipboard(password)
        except ClipboardError as exc:
            # Non-fatal: password was still generated successfully.
            messagebox.showwarning("Clipboard Warning", str(exc))

    def on_copy_click(self) -> None:
        """Handle the manual 'Copy Password' button click."""
        password = self.password_var.get()
        try:
            copy_to_clipboard(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        except ClipboardError as exc:
            messagebox.showerror("Clipboard Error", str(exc))

    def on_history_select(self, _event) -> None:
        """When a history entry is clicked, display and copy it."""
        selection = self.history_listbox.curselection()
        if not selection:
            return
        password = self.history_listbox.get(selection[0])
        self.password_var.set(password)
        self._update_strength_indicator(password)

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------
    def _get_validated_length(self) -> int:
        """
        Retrieve and validate the password length from the GUI input.

        Raises:
            PasswordGeneratorError: If the input is not a valid integer
            within the allowed range.
        """
        raw_value = self.length_spinbox.get()
        try:
            length = int(raw_value)
        except ValueError:
            raise PasswordGeneratorError(
                "Password length must be a whole number."
            )

        if length < PasswordGenerator.MIN_LENGTH or length > PasswordGenerator.MAX_LENGTH:
            raise PasswordGeneratorError(
                f"Password length must be between {PasswordGenerator.MIN_LENGTH} "
                f"and {PasswordGenerator.MAX_LENGTH}."
            )
        return length

    def _update_strength_indicator(self, password: str) -> None:
        """Update the strength label and colored bar based on the password."""
        label, color = StrengthChecker.evaluate(password)
        self.strength_label_var.set(f"Strength: {label}")
        self.strength_display.configure(fg=color)
        self.strength_bar.configure(bg=color)

    def _refresh_history_display(self) -> None:
        """Refresh the Listbox to reflect the current session history."""
        self.history_listbox.delete(0, tk.END)
        for entry in self.history_manager.get_all():
            self.history_listbox.insert(tk.END, entry)


def main() -> None:
    """Application entry point."""
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
