import logging
import json

logger = logging.getLogger(__name__)


class Nutrition:
    """Фитнес расчёты уровня V3"""

    def calculate_calories(self, weight, height, age, gender, goal):
        # Mifflin-St Jeor
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity = 1.3
        tdee = int(bmr * activity)

        if goal == "loss":
            calories = tdee - 500
        elif goal == "gain":
            calories = tdee + 300
        else:
            calories = tdee

        protein = int(weight * 2)
        fats = int(weight * 0.8)
        carbs = int((calories - (protein * 4 + fats * 9)) / 4)

        return {
            "bmr": int(bmr),
            "tdee": tdee,
            "calories": calories,
            "protein": protein,
            "fats": fats,
            "carbs": carbs
        }

    def get_nutrition_plan(self, goal):
        if goal == "loss":
            return {
                "title": "🔥 ПОХУДЕНИЕ",
                "desc": "Дефицит калорий - жиросжигание",
                "example": {
                    "breakfast": "яйца + овсянка",
                    "lunch": "курица + овощи",
                    "dinner": "рыба + салат"
                }
            }

        if goal == "gain":
            return {
                "title": "💪 МАССА",
                "desc": "Профицит калорий - рост мышц",
                "example": {
                    "breakfast": "овсянка + банан + яйца",
                    "lunch": "рис + курица",
                    "dinner": "паста + мясо"
                }
            }

        return {
            "title": "⚖️ ПОДДЕРЖАНИЕ",
            "desc": "Баланс формы",
            "example": {
                "breakfast": "яйца + каша",
                "lunch": "мясо + крупа",
                "dinner": "рыба + овощи"
            }
        }