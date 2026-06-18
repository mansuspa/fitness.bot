import logging
from datetime import datetime
from config import WORKOUTS_FILE

logger = logging.getLogger(__name__)

class Workout:
    """Класс для работы с тренировками"""
    
    def __init__(self):
        self.workouts_file = WORKOUTS_FILE
        self.workouts = self._load_workouts()
    
    def _load_workouts(self):
        """Загрузка тренировок из файла"""
        try:
            with open(self.workouts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Файл тренировок не найден, создаю новый")
            return {
                "gain": {
                    "upper_body": [],
                    "lower_body": [],
                    "cardio": [],
                    "rest": []
                },
                "loss": {
                    "upper_body": [],
                    "lower_body": [],
                    "cardio": [],
                    "rest": []
                }
            }
        except json.JSONDecodeError:
            logger.error("Ошибка чтения файла тренировок")
            return {
                "gain": {
                    "upper_body": [],
                    "lower_body": [],
                    "cardio": [],
                    "rest": []
                },
                "loss": {
                    "upper_body": [],
                    "lower_body": [],
                    "cardio": [],
                    "rest": []
                }
            }
    
    def _save_workouts(self):
        """Сохранение тренировок в файл"""
        try:
            with open(self.workouts_file, 'w', encoding='utf-8') as f:
                json.dump(self.workouts, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.workouts)} тренировок")
        except Exception as e:
            logger.error(f"Ошибка сохранения тренировок: {e}")
    
    def get_gain_workout_plan(self):
        """План тренировок для набора массы"""
        plan = {
            "upper_body": [
                "Жим лёжа - 4 подхода по 8-12 повторений",
                "Подтягивания - 4 подхода по 6-10 повторений",
                "Жим гантелей сидя - 3 подхода по 10-12 повторений",
                "Отжимания - 3 подхода по 12-15 повторений",
                "Тяга штанги в наклоне - 4 подхода по 8-10 повторений",
                "Разведение гантелей в стороны - 3 подхода по 12-15 повторений"
            ],
            "lower_body": [
                "Приседания со штангой - 4 подхода по 8-10 повторений",
                "Становая тяга - 4 подхода по 6-8 повторений",
                "Выпады с гантелями - 3 подхода по 10-12 повторений на ногу",
                "Подъём на носки - 4 подхода по 15-20 повторений",
                "Румынская тяга - 3 подхода по 10-12 повторений"
            ],
            "cardio": [
                "Бег - 15-20 минут",
                "Велосипед - 15-20 минут",
                "Эллипсоид - 15-20 минут"
            ],
            "rest": [
                "Отдых 2-3 минуты между подходами",
                "Полный отдых 48-72 часа между тренировками"
            ]
        }
        return plan
    
    def get_loss_workout_plan(self):
        """План тренировок для похудения"""
        plan = {
            "upper_body": [
                "Отжимания - 3 подхода по 15-20 повторений",
                "Жим гантелей лёжа - 3 подхода по 12-15 повторений",
                "Тяга гантели одной рукой - 3 подхода по 12-15 повторений",
                "Планка - 3 подхода по 30-60 секунд",
                "Подтягивания (или тяга верхнего блока) - 3 подхода по 10-15 повторений"
            ],
            "lower_body": [
                "Выпады - 3 подхода по 12-15 повторений на ногу",
                "Приседания без веса - 3 подхода по 20-30 повторений",
                "Ягодичный мостик - 3 подхода по 15-20 повторений",
                "Подъём на носки - 3 подхода по 20-30 повторений",
                "Бёрпи - 3 подхода по 10-15 повторений"
            ],
            "cardio": [
                "Бег - 30-40 минут",
                "Интервальный бег - 20 минут (30 сек бег, 30 сек ходьба)",
                "Велосипед - 30-40 минут",
                "Эллипсоид - 30-40 минут"
            ],
            "rest": [
                "Отдых 60-90 секунд между подходами",
                "Полный отдых 48 часов между тренировками"
            ]
        }
        return plan
    
    def get_workout_plan_text(self, goal: str):
        """Получение текста плана тренировок"""
        if goal == "gain":
            plan = self.get_gain_workout_plan()
            text = "💪 **План тренировок для НАБОРА МАССЫ**\n\n"
            text += "**Тип тренировки:** Силовая (3-4 раза в неделю)\n\n"
        else:
            plan = self.get_loss_workout_plan()
            text = "💪 **План тренировок для ПОХУДЕНИЯ**\n\n"
            text += "**Тип тренировки:** Силовая + кардио (4-5 раз в неделю)\n\n"
        
        for category, exercises in plan.items():
            text += f"**{category.title()}:**\n"
            for exercise in exercises:
                text += f"- {exercise}\n"
            text += "\n"
        
        return text
    
    def add_workout(self, goal: str, category: str, workout_dict):
        """Добавление тренировки"""
        if goal in self.workouts and category in self.workouts[goal]:
            self.workouts[goal][category].append(workout_dict)
            self._save_workouts()
            logger.info(f"Добавлена тренировка: {goal} - {category}")
    
    def get_workouts(self, goal: str = None, category: str = None):
        """Получение тренировок"""
        if goal:
            if category:
                return self.workouts.get(goal, {}).get(category, [])
            return self.workouts.get(goal, {})
        return self.workouts
    
    def get_workout_plan(self):
        """Получение полного плана тренировок"""
        return self.workouts