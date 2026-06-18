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
    
    def calculate_calories(self, weight: float, height: float, age: int, gender: str):
        """Расчёт калорий по формуле Миффлина-Сан Жеора"""
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Коэффициент активности
        activity_multiplier = 1.2  # По умолчанию - малая активность
        
        # Расчёт суточной нормы
        daily_calories = int(bmr * activity_multiplier)
        
        return {
            "bmr": int(bmr),
            "daily_calories": daily_calories,
            "activity_multiplier": activity_multiplier
        }
    
    def create_meal_plan(self, calories: int, goal: str):
        """Создание плана питания"""
        # Распределение калорий
        if goal == "gain":
            # Для набора массы - больше углеводов
            meal_plan = {
                "breakfast": {
                    "calories": int(calories * 0.30),
                    "description": "Завтрак: белки, сложные углеводы, клетчатка"
                },
                "lunch": {
                    "calories": int(calories * 0.35),
                    "description": "Обед: белки, овощи, сложные углеводы"
                },
                "dinner": {
                    "calories": int(calories * 0.25),
                    "description": "Ужин: белки, овощи, углеводы"
                },
                "snacks": {
                    "calories": int(calories * 0.10),
                    "description": "Перекусы: орехи, творог, фрукты"
                }
            }
        else:
            # Для похудения - меньше углеводов
            meal_plan = {
                "breakfast": {
                    "calories": int(calories * 0.25),
                    "description": "Завтрак: белки, клетчатка, немного углеводов"
                },
                "lunch": {
                    "calories": int(calories * 0.35),
                    "description": "Обед: белки, овощи, мало углеводов"
                },
                "dinner": {
                    "calories": int(calories * 0.30),
                    "description": "Ужин: белки, овощи, минимум углеводов"
                },
                "snacks": {
                    "calories": int(calories * 0.10),
                    "description": "Перекусы: фрукты, белки, зелень"
                }
            }
        
        return meal_plan
    
    def get_meal_plan_text(self, calories: int, goal: str):
        """Получение текста плана питания"""
        meal_plan = self.create_meal_plan(calories, goal)
        
        text = f"🍽️ **План питания для {goal}**\n\n"
        text += f"**Суточная норма: {calories} ккал**\n\n"
        
        for meal_type, meal_data in meal_plan.items():
            text += f"**{meal_type.title()}:** {meal_data['calories']} ккал\n"
            text += f"{meal_data['description']}\n\n"
        
        return text
    
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