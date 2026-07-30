"""Streamlit web interface for the BMI Calculator."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import streamlit as st

from bmi import BMIResult, BMICalculator
from database import DatabaseManager
from utils import current_timestamp, parse_positive_number, validate_name


PROJECT_DIRECTORY = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIRECTORY / "bmi_database.db"


def get_database() -> DatabaseManager:
    """Return a connected database manager for the Streamlit session."""
    database = DatabaseManager(DATABASE_PATH)
    database.initialize()
    return database


def reset_result() -> None:
    """Clear the result stored in the current Streamlit session."""
    st.session_state.pop("current_result", None)
    st.session_state.pop("current_inputs", None)


def calculate_from_form(username_value: str, weight_value: str, height_value: str) -> tuple[str, float, float, BMIResult]:
    """Validate form values and calculate a BMI result."""
    username = validate_name(username_value)
    weight = parse_positive_number(weight_value, "Weight", 500)
    height = parse_positive_number(height_value, "Height", 3)
    result = BMICalculator().calculate(weight, height)
    return username, weight, height, result


def show_result(result: BMIResult) -> None:
    """Render the BMI result card with the category color."""
    category_color = BMICalculator.color_for(result.category)
    st.markdown(
        f"""
        <div class="result-card" style="border-left-color: {category_color};">
            <div class="result-label">YOUR BMI</div>
            <div class="result-value" style="color: {category_color};">{result.bmi:.2f}</div>
            <div class="result-category" style="color: {category_color};">{result.category}</div>
            <div class="result-message">{result.health_message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trend(records: list[dict[str, Any]], title: str) -> None:
    """Render a Matplotlib BMI trend chart inside Streamlit."""
    if not records:
        st.info("No BMI records are available for the selected user.")
        return

    ordered_records = sorted(records, key=lambda record: record["date"])
    dates = [record["date"] for record in ordered_records]
    values = [float(record["bmi"]) for record in ordered_records]

    figure, axis = plt.subplots(figsize=(10, 4.8))
    figure.patch.set_facecolor("#f8fafc")
    axis.set_facecolor("#ffffff")
    axis.plot(
        dates,
        values,
        color="#1976d2",
        marker="o",
        markersize=7,
        linewidth=2.5,
        label="BMI",
    )
    axis.set_title(title, fontsize=16, fontweight="bold", color="#16324f", pad=14)
    axis.set_xlabel("Date")
    axis.set_ylabel("BMI")
    axis.grid(True, linestyle="--", alpha=0.35)
    axis.legend(loc="best")
    figure.autofmt_xdate()
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)


def render_history(database: DatabaseManager) -> None:
    """Render the history table for one user or all users."""
    default_user = st.session_state.get("last_username", "")
    history_user_value = st.text_input(
        "History user name",
        value=default_user,
        key="history_user",
        help="Leave blank to view every saved record.",
    )
    try:
        history_user = validate_name(history_user_value) if history_user_value.strip() else None
        records = database.get_records(history_user)
    except ValueError as error:
        st.error(str(error))
        return

    if not records:
        st.info("No BMI records found for the selected user.")
        return

    table_rows = [
        {
            "Date": record["date"],
            "User": record["username"],
            "Weight (kg)": f"{record['weight']:.2f}",
            "Height (m)": f"{record['height']:.2f}",
            "BMI": f"{record['bmi']:.2f}",
            "Category": record["category"],
        }
        for record in records
    ]
    st.dataframe(table_rows, use_container_width=True, hide_index=True)


def render_app() -> None:
    """Render the complete Streamlit application."""
    st.set_page_config(page_title="BMI Calculator", page_icon="⚖️", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: #f4f7fb; }
        .block-container { max-width: 1100px; padding-top: 2rem; }
        .hero { background: linear-gradient(135deg, #16324f, #1976d2); color: white;
                padding: 2rem 2.2rem; border-radius: 18px; margin-bottom: 1.4rem; }
        .hero h1 { margin: 0; font-size: 2.5rem; }
        .hero p { margin: .45rem 0 0; opacity: .88; font-size: 1.05rem; }
        .result-card { background: white; border-left: 8px solid #1976d2; border-radius: 14px;
                       padding: 1.3rem 1.5rem; box-shadow: 0 2px 12px rgba(22,50,79,.08); }
        .result-label { color: #607d8b; font-size: .8rem; font-weight: 700; letter-spacing: .08em; }
        .result-value { font-size: 3.4rem; font-weight: 800; line-height: 1.1; }
        .result-category { font-size: 1.25rem; font-weight: 700; margin-bottom: .75rem; }
        .result-message { color: #546e7a; font-size: .98rem; }
        </style>
        <div class="hero">
            <h1>⚖️ BMI Calculator</h1>
            <p>Calculate your BMI, save your history, and understand your progress over time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    database = get_database()
    current_result: BMIResult | None = st.session_state.get("current_result")

    input_column, result_column = st.columns([1, 1], gap="large")
    with input_column:
        st.subheader("Calculate BMI")
        with st.form("bmi_form", clear_on_submit=False):
            username = st.text_input("User name", value=st.session_state.get("last_username", ""), placeholder="e.g. Alex Johnson")
            weight = st.text_input("Weight (kg)", placeholder="e.g. 68.5")
            height = st.text_input("Height (meters)", placeholder="e.g. 1.72")
            calculate_clicked, save_clicked = st.columns(2)
            with calculate_clicked:
                calculate_button = st.form_submit_button("Calculate BMI", use_container_width=True, type="primary")
            with save_clicked:
                save_button = st.form_submit_button("Save Record", use_container_width=True)

        if calculate_button or save_button:
            try:
                valid_username, valid_weight, valid_height, result = calculate_from_form(username, weight, height)
                st.session_state["last_username"] = valid_username
                st.session_state["current_inputs"] = (valid_username, valid_weight, valid_height)
                st.session_state["current_result"] = result
                current_result = result
                if save_button:
                    database.save_record(
                        valid_username,
                        valid_weight,
                        valid_height,
                        result.bmi,
                        result.category,
                        current_timestamp(),
                    )
                    st.success(f"BMI record saved for {valid_username}.")
                else:
                    st.success("BMI calculated successfully.")
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"Unable to process the BMI record: {error}")

        if st.button("Clear result", use_container_width=True):
            reset_result()
            st.rerun()

    with result_column:
        st.subheader("Your Result")
        if current_result:
            show_result(current_result)
        else:
            st.info("Enter your details and click Calculate BMI to see your result.")

    st.divider()
    history_tab, trend_tab = st.tabs(["📋 BMI History", "📈 BMI Trend"])
    with history_tab:
        render_history(database)
    with trend_tab:
        trend_user_value = st.text_input(
            "Trend user name",
            value=st.session_state.get("last_username", ""),
            key="trend_user",
            help="Leave blank to show the combined trend for all users.",
        )
        try:
            trend_user = validate_name(trend_user_value) if trend_user_value.strip() else None
            trend_records = database.get_records(trend_user)
            trend_title = f"BMI Trend — {trend_user}" if trend_user else "BMI Trend — All Users"
            render_trend(trend_records, trend_title)
        except ValueError as error:
            st.error(str(error))

    st.caption("BMI is a screening measure, not a diagnosis. Consult a qualified healthcare professional for personalized advice.")


if __name__ == "__main__":
    render_app()
