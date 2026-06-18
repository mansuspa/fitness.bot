import logging
from datetime import datetime
from config import MEALS_FILE

logger = logging.getLogger(__name__)

class Nutrition:
    """Класс для работы с питанием"""
    
    def __init__(self):
        self.meals_file = MEALS_FILE
        self.meals = self._load_meals()
    
    def _load_meals(self):
        """Загрузка рационов из файла"""
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
            logger.error("Ошибка чтения файла рационов")
            return {
                "breakfast": [],
                "lunch": [],
                "dinner": [],
                "snacks": []
            }
    
    def _save_meals(self):
        """Сохранение рационов в файл"""
        try:
            with open(self.meals_file, 'w', encoding='utf-8') as f:
                json.dump(self.meals, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.meals)} рационов")
        except Exception as e:
            logger.error(f"Ошибка сохранения рационов: {e}")
    
    def calculate_calories(self, weight: float, height: float, age: int, gender: str, goal: str):
        """Расчёт калорий по формуле Миффлина-Сан Жеора"""
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Коэффициент активности
        activity_multiplier = 1.2  # По умолчанию - малая активность
        
        # Расчёт суточной нормы
        daily_calories = int(bmr * activity_multiplier)
        
        # Корректировка под цель
        if goal == 'gain':
            daily_calories += 300  # Для набора
        elif goal == 'loss':
            daily_calories -= 500  # Для похудения
        
        return {
            "bmr": int(bmr),
            "daily_calories": daily_calories,
            "activity_multiplier": activity_multiplier,
            "goal": goal
        }
    
    def get_nutrition_plan(self, goal: str):
        """Получение плана питания для цели"""
        if goal == 'gain':
            return {
                "title": "💪 План питания для НАБОРА мышечной массы",
                "description": "Увеличение калорийности на 300 ккал для набора массы",
                "macros": {
                    "protein": "1.6-2.0 г/кг",
                    "carbs": "4-6 г/кг",
                    "fats": "1-1.2 г/кг"
                },
                "meals": {
                    "breakfast": [
                        "Овсянка с молоком и орехами",
                        "Яйца (2-3 шт.)",
                        "Творог",
                        "Банан"
                    ],
                    "lunch": [
                        "Куриное филе (200г)",
                        "Рис (150г)",
                        "Овощной салат",
                        "Оливковое масло"
                    ],
                    "dinner": [
                        "Рыба (200г)",
                        "Картофель (150г)",
                        "Овощи",
                        "Сметана"
                    ],
                    "snacks": [
                        "Греческий йогурт",
                        "Орехи (30г)",
                        "Фрукты",
                        "Протеиновый коктейль"
                    ]
                }
            }
        elif goal == 'loss':
            return {
                "title": "🔥 План питания для ПОХУДЕНИЯ",
                "description": "Уменьшение калорийности на 500 ккал для похудения",
                "macros": {
                    "protein": "1.8-2.2 г/кг",
                    "carbs": "2-3 г/кг",
                    "fats": "0.8-1 г/кг"
                },
                "meals": {
                    "breakfast": [
                        "Гречка с яйцом",
                        "Творог",
                        "Яблоко",
                        "Кофе/чай без сахара"
                    ],
                    "lunch": [
                        "Индейка (150г)",
                        "Гречка (100г)",
                        "Овощной салат",
                        "Оливковое масло (1 ст.л.)"
                    ],
                    "dinner": [
                        "Кальмар (150г)",
                        "Капуста (200г)",
                        "Творог (100г)",
                        "Овощи"
                    ],
                    "snacks": [
                        "Ягоды",
                        "Творог (100г)",
                        "Орехи (15г)",
                        "Яйцо (варёное)"
                    ]
                }
            }
        else:
            return {
                "title": "⚖️ План питания для ПОДДЕРЖАНИЯ",
                "description": "Поддержание текущего веса",
                "macros": {
                    "protein": "1.6-1.8 г/кг",
                    "carbs": "3-4 г/кг",
                    "fats": "0.9-1 г/кг"
                },
                "meals": {
                    "breakfast": [
                        "Овсянка",
                        "Яйца",
                        "Творог",
                        "Фрукты"
                    ],
                    "lunch": [
                        "Курица/рыба",
                        "Гречка/рис",
                        "Овощи",
                        "Масло"
                    ],
                    "dinner": [
                        "Белковое блюдо",
                        "Овощи",
                        "Кисломолочные продукты"
                    ],
                    "snacks": [
                        "Йогурт",
                        "Фрукты",
                        "Орехи"
                    ]
                }
            }
    
    def add_meal(self, meal_type: str, meal_dict):
        """Добавление приёма пищи"""
        if meal_type in self.meals:
            self.meals[meal_type].append(meal_dict)
            self._save_meals()
            logger.info(f"Добавлен приём пищи: {meal_type}")
    
    def get_meals(self, meal_type: str = None):
        """Получение приёмов пищи"""
        if meal_type:
            return self.meals.get(meal_type, [])
        return self.meals
    
    def get_meal_plan(self):
        """Получение полного плана питания"""
        return self.meals