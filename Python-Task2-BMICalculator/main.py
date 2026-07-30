"""Application entry point for the BMI Calculator."""

from pathlib import Path

from gui import launch_app


if __name__ == "__main__":
    project_directory = Path(__file__).resolve().parent
    launch_app(project_directory / "bmi_database.db")
