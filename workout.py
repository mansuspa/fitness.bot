import logging
import json
from config import WORKOUTS_FILE

logger = logging.getLogger(__name__)


class Workout:
    """Фитнес тренировки"""

    def __init__(self):
        self.file = WORKOUTS_FILE
        self.workouts = self._load()

    def _load(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(self.workouts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Save error: {e}")

    def get_workout_plan(self, goal: str):
        """Планы тренировок"""

        if goal == "gain":
            return {
                "title": "💪 НАБОР МАССЫ",
                "days": {
                    "Понедельник": "Грудь + трицепс",
                    "Вторник": "Спина + бицепс",
                    "Среда": "Ноги",
                    "Четверг": "Отдых",
                    "Пятница": "Плечи + руки",
                    "Суббота": "Кардио",
                    "Воскресенье": "Отдых"
                },
                "exercises": {
                    "Грудь": [
                        "Жим лёжа 4×8-10",
                        "Жим гантелей 3×10",
                        "Разводка 3×12"
                    ],
                    "Спина": [
                        "Подтягивания 4×макс",
                        "Тяга штанги 4×10",
                        "Тяга блока 3×12"
                    ],
                    "Ноги": [
                        "Присед 4×8-10",
                        "Жим ногами 4×12",
                        "Выпады 3×12"
                    ]
                }
            }

        if goal == "loss":
            return {
                "title": "🔥 ПОХУДЕНИЕ",
                "days": {
                    "Понедельник": "Кардио + пресс",
                    "Вторник": "Грудь + спина",
                    "Среда": "HIIT",
                    "Четверг": "Ноги",
                    "Пятница": "Кардио",
                    "Суббота": "Фулбади",
                    "Воскресенье": "Отдых"
                },
                "exercises": {
                    "Кардио": [
                        "Бег 30 мин",
                        "Скакалка 15 мин",
                        "HIIT 20 мин"
                    ],
                    "Пресс": [
                        "Скручивания 4×20",
                        "Планка 3×60 сек",
                        "Подъём ног 4×15"
                    ]
                }
            }

        return {
            "title": "⚖️ ПОДДЕРЖАНИЕ",
            "days": {
                "Понедельник": "Фулбади",
                "Среда": "Фулбади",
                "Пятница": "Фулбади",
                "Остальные": "Отдых"
            },
            "exercises": {
                "Фулбади": [
                    "Жим лёжа 3×10",
                    "Присед 3×10",
                    "Тяга 3×10",
                    "Жим гантелей 3×12"
                ]
            }
        }