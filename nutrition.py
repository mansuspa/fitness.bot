import logging

logger = logging.getLogger(__name__)


class Nutrition:
    """Фитнес питание (стабильная версия)"""

    def calculate_calories(self, weight, height, age, gender, goal):
        # Mifflin-St Jeor formula
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity = 1.4  # средняя активность
        tdee = int(bmr * activity)

        # корректировка под цель
        if goal == "loss":
            calories = tdee - 400
        elif goal == "gain":
            calories = tdee + 300
        else:
            calories = tdee

        protein = int(weight * 2)
        fats = int(weight * 0.9)
        carbs = int((calories - (protein * 4 + fats * 9)) / 4)

        return {
            "bmr": int(bmr),
            "tdee": tdee,
            "calories": calories,
            "protein": protein,
            "fats": fats,
            "carbs": carbs
        }

    # ---------------- ПИТАНИЕ ----------------

    def food_guide(self):
        return {
            "loss": {
                "title": "🔥 ПОХУДЕНИЕ (жиросжигание)",
                "rules": [
                    "дефицит -300 / -500 ккал",
                    "высокий белок",
                    "минимум сахара",
                    "2-3 литра воды"
                ],
                "macros": {
                    "protein": "1.8-2.2 г/кг",
                    "fats": "0.8-1 г/кг",
                    "carbs": "2-3 г/кг"
                },
                "foods": {
                    "protein": ["курица", "рыба", "яйца", "творог"],
                    "carbs": ["гречка", "рис", "овсянка"],
                    "fats": ["орехи", "оливковое масло"],
                    "extra": ["овощи", "зелень"]
                },
                "avoid": [
                    "сахар",
                    "фастфуд",
                    "соки",
                    "выпечка"
                ]
            },

            "gain": {
                "title": "💪 НАБОР МАССЫ",
                "rules": [
                    "профицит +300-500 ккал",
                    "4-5 приёмов пищи",
                    "углеводы = энергия",
                    "белок каждый приём"
                ],
                "macros": {
                    "protein": "2-2.2 г/кг",
                    "fats": "1 г/кг",
                    "carbs": "4-6 г/кг"
                },
                "foods": {
                    "protein": ["курица", "говядина", "яйца", "рыба"],
                    "carbs": ["рис", "паста", "овсянка", "бананы"],
                    "fats": ["орехи", "масло", "авокадо"],
                    "extra": ["молоко", "йогурт"]
                },
                "tip": "ешь каждые 3-4 часа"
            },

            "maintain": {
                "title": "⚖️ ПОДДЕРЖАНИЕ ФОРМЫ",
                "rules": [
                    "калории = норма",
                    "баланс БЖУ",
                    "без дефицита"
                ],
                "macros": {
                    "protein": "1.6-2 г/кг",
                    "fats": "0.9-1 г/кг",
                    "carbs": "3-4 г/кг"
                },
                "foods": {
                    "protein": ["мясо", "рыба", "яйца"],
                    "carbs": ["крупы", "овощи", "фрукты"],
                    "fats": ["орехи", "масло"],
                    "extra": ["молочные продукты"]
                }
            }
        }