"""BMI calculation and classification logic."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BMIResult:
    """Immutable result returned by :class:`BMICalculator`."""

    bmi: float
    category: str
    health_message: str


class BMICalculator:
    """Calculate BMI values and translate them into health categories."""

    CATEGORY_COLORS = {
        "Underweight": "#1976d2",
        "Normal Weight": "#2e7d32",
        "Overweight": "#ef6c00",
        "Obese": "#c62828",
    }

    def calculate(self, weight: float, height: float) -> BMIResult:
        """Return a rounded BMI result for a weight in kg and height in m."""
        if height <= 0:
            raise ValueError("Height must be greater than zero.")
        bmi = round(weight / (height**2), 2)
        category, message = self.classify(bmi)
        return BMIResult(bmi, category, message)

    @staticmethod
    def classify(bmi: float) -> tuple[str, str]:
        """Classify a BMI using standard adult BMI ranges."""
        if bmi < 18.5:
            return "Underweight", "Consider a balanced nutrition plan and regular exercise."
        if bmi < 25:
            return "Normal Weight", "Great work! Maintain your balanced lifestyle."
        if bmi < 30:
            return "Overweight", "Regular activity and balanced meals can support your health."
        return "Obese", "Consider speaking with a healthcare professional for personalized guidance."

    @classmethod
    def color_for(cls, category: str) -> str:
        """Return the display color assigned to a BMI category."""
        return cls.CATEGORY_COLORS.get(category, "#263238")
