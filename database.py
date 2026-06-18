import json
import logging
from datetime import datetime
from config import DB_FILE

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self.users = self._load_users()
    
    def _load_users(self):
        """Загрузка пользователей из файла"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Файл базы данных не найден, создаю новый")
            return {}
        except json.JSONDecodeError:
            logger.error("Ошибка чтения файла базы данных")
            return {}
    
    def _save_users(self):
        """Сохранение пользователей в файл"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.users)} пользователей")
        except Exception as e:
            logger.error(f"Ошибка сохранения базы данных: {e}")
    
    def add_user(self, user_id: int, username: str):
        """Добавление пользователя"""
        if user_id not in self.users:
            self.users[user_id] = {
                'user_id': user_id,
                'username': username,
                'created_at': datetime.now().isoformat(),
                'weight': None,
                'height': None,
                'age': None,
                'goal': None
            }
            self._save_users()
            logger.info(f"Пользователь {username} добавлен")
    
    def get_user(self, user_id: int):
        """Получение информации о пользователе"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: int, **kwargs):
        """Обновление информации о пользователе"""
        if user_id in self.users:
            for key, value in kwargs.items():
                if key in self.users[user_id]:
                    self.users[user_id][key] = value
            self._save_users()
            logger.info(f"Информация о пользователе {user_id} обновлена")
    
    def get_all_users(self):
        """Получение списка всех пользователей"""
        return list(self.users.values())
    
    def delete_user(self, user_id: int):
        """Удаление пользователя"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            logger.info(f"Пользователь {user_id} удалён")