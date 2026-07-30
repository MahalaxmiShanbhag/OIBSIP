"""Matplotlib BMI trend visualization."""

from collections import defaultdict
from datetime import datetime
from tkinter import Toplevel, ttk
from typing import Any


class GraphManager:
    """Create and display BMI trend charts in a Tkinter window."""

    def show_trend(
        self,
        parent: Any,
        records: list[dict[str, Any]],
        title: str = "BMI Trend",
    ) -> None:
        """Display a date-sorted line graph for the supplied records."""
        if not records:
            raise ValueError("No BMI records are available for the selected user.")

        try:
            import matplotlib.dates as mdates
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
        except ImportError as error:
            raise RuntimeError("Matplotlib is not installed. Run: pip install -r requirements.txt") from error

        grouped_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            grouped_records[record.get("username", "BMI")].append(record)

        graph_window = Toplevel(parent)
        graph_window.title(title)
        graph_window.geometry("900x600")
        graph_window.minsize(700, 450)

        figure = Figure(figsize=(9, 5.5), dpi=100, facecolor="#f8fafc")
        axis = figure.add_subplot(111)
        axis.set_facecolor("#ffffff")
        palette = ["#1976d2", "#2e7d32", "#ef6c00", "#8e44ad", "#c62828"]

        for index, (username, user_records) in enumerate(sorted(grouped_records.items())):
            ordered = sorted(user_records, key=lambda item: item["date"])
            dates = [datetime.strptime(item["date"], "%Y-%m-%d %H:%M:%S") for item in ordered]
            values = [float(item["bmi"]) for item in ordered]
            axis.plot(
                dates,
                values,
                marker="o",
                linewidth=2.2,
                markersize=6,
                color=palette[index % len(palette)],
                label=username,
            )

        axis.set_title(title, fontsize=16, fontweight="bold", color="#263238", pad=14)
        axis.set_xlabel("Date", fontsize=11)
        axis.set_ylabel("BMI", fontsize=11)
        axis.grid(True, linestyle="--", alpha=0.35)
        axis.legend(loc="best", frameon=True)
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        figure.autofmt_xdate()
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(12, 4))
        ttk.Label(
            graph_window,
            text="BMI reference: Underweight < 18.5  |  Normal 18.5–24.9  |  Overweight 25–29.9  |  Obese ≥ 30",
            anchor="center",
        ).pack(fill="x", padx=12, pady=(0, 10))
