import json
import logging

logger = logging.getLogger(__name__)

class Nutrition:
    """FITNESS AI nutrition module (V7 PRO)"""

    def __init__(self):
        self.data = {
            "gain": {
                "title": "💪 НАБОР МАССЫ",
                "calories_multiplier": 1.15,
                "macros": {
                    "protein": "1.8-2.2 г/кг",
                    "carbs": "4-6 г/кг",
                    "fats": "1-1.2 г/кг"
                },
                "meals": {
                    "breakfast": ["овсянка", "яйца", "банан"],
                    "lunch": ["рис", "курица", "овощи"],
                    "dinner": ["рыба", "картофель", "салат"],
                    "snacks": ["творог", "орехи", "йогурт"]
                },
                "tips": [
                    "Ешь +300–500 ккал в день",
                    "Принимай белок в каждом приёме пищи",
                    "Пей 2–3 литра воды"
                ]
            },

            "loss": {
                "title": "🔥 ПОХУДЕНИЕ",
                "calories_multiplier": 0.85,
                "macros": {
                    "protein": "2.0-2.4 г/кг",
                    "carbs": "2-3 г/кг",
                    "fats": "0.8-1 г/кг"
                },
                "meals": {
                    "breakfast": ["яйца", "овсянка", "яблоко"],
                    "lunch": ["курица", "гречка", "овощи"],
                    "dinner": ["рыба", "овощи", "творог"],
                    "snacks": ["йогурт", "ягоды", "орехи (мал.)"]
                },
                "tips": [
                    "Дефицит -300/-500 ккал",
                    "Убери сахар и фастфуд",
                    "Кардио 3–5 раз в неделю"
                ]
            },

            "maintain": {
                "title": "⚖️ ПОДДЕРЖАНИЕ",
                "calories_multiplier": 1.0,
                "macros": {
                    "protein": "1.6-2.0 г/кг",
                    "carbs": "3-4 г/кг",
                    "fats": "1 г/кг"
                },
                "meals": {
                    "breakfast": ["овсянка", "яйца"],
                    "lunch": ["мясо", "крупа", "овощи"],
                    "dinner": ["рыба", "овощи"],
                    "snacks": ["йогурт", "фрукты"]
                },
                "tips": [
                    "Держи баланс калорий",
                    "3 тренировки в неделю",
                    "Не переедай"
                ]
            }
        }

    # ---------------- MAIN ----------------
    def get_nutrition_plan(self, goal: str):
        return self.data.get(goal, self.data["maintain"])

    # ---------------- CALORIES ----------------
    def calculate_calories(self, weight: float, height: float, age: int, goal: str = "maintain"):
        """Mifflin-St Jeor formula"""

        # базовый обмен
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

        plan = self.data.get(goal, self.data["maintain"])
        calories = int(bmr * plan["calories_multiplier"])

        return {
            "bmr": int(bmr),
            "calories": calories,
            "goal": goal
        }

    # ---------------- SIMPLE FOOD GUIDE ----------------
    def food(self, goal: str):
        return self.data