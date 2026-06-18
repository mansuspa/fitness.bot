import logging
import json
from datetime import datetime
from config import MEALS_FILE

logger = logging.getLogger(__name__)


class Nutrition:
    """Класс для работы с питанием"""

    def __init__(self):
        self.meals_file = MEALS_FILE
        self.meals = self._load_meals()

    def _load_meals(self):
        try:
            with open(self.meals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Файл рационов не найден, создаю новый")
            return {
                "breakfast": [],
                "lunch": [],
                "dinner": [],
                "snacks": []
            }
        except json.JSONDecodeError:
            logger.error("Ошибка чтения рационов")
            return {
                "breakfast": [],
                "lunch": [],
                "dinner": [],
                "snacks": []
            }

    def _save_meals(self):
        try:
            with open(self.meals_file, 'w', encoding='utf-8') as f:
                json.dump(self.meals, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения рационов: {e}")

    def calculate_calories(self, weight, height, age, gender, goal):
        """Калории (Mifflin-St Jeor)"""

        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity = 1.2
        calories = int(bmr * activity)

        if goal == "gain":
            calories += 300
        elif goal == "loss":
            calories -= 500

        return {
            "bmr": int(bmr),
            "calories": calories,
            "goal": goal
        }

    def get_nutrition_plan(self, goal):
        """Готовый план питания"""

        if goal == "gain":
            return {
                "title": "💪 НАБОР МАССЫ",
                "macros": {
                    "protein": "1.6-2.0 г/кг",
                    "carbs": "4-6 г/кг",
                    "fats": "1-1.2 г/кг"
                },
                "meals": {
                    "breakfast": "Овсянка + яйца + банан",
                    "lunch": "Курица 200г + рис 150г",
                    "dinner": "Рыба 200г + овощи",
                    "snacks": "Творог + орехи"
                }
            }

        if goal == "loss":
            return {
                "title": "🔥 ПОХУДЕНИЕ",
                "macros": {
                    "protein": "1.8-2.2 г/кг",
                    "carbs": "2-3 г/кг",
                    "fats": "0.8-1 г/кг"
                },
                "meals": {
                    "breakfast": "Яйца + гречка",
                    "lunch": "Индейка 150г + овощи",
                    "dinner": "Рыба + салат",
                    "snacks": "Йогурт"
                }
            }

        return {
            "title": "⚖️ ПОДДЕРЖАНИЕ",
            "macros": {
                "protein": "1.6-1.8 г/кг",
                "carbs": "3-4 г/кг",
                "fats": "0.9-1 г/кг"
            },
            "meals": {
                "breakfast": "Овсянка + яйца",
                "lunch": "Курица + гречка",
                "dinner": "Рыба + овощи",
                "snacks": "Фрукты"
            }
        }

    def add_meal(self, meal_type, meal):
        if meal_type not in self.meals:
            self.meals[meal_type] = []

        self.meals[meal_type].append(meal)
        self._save_meals()

    def get_meal_plan(self):
        return self.meals