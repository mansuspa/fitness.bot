import json
import logging
from datetime import datetime
from config import DB_FILE

logger = logging.getLogger(__name__)


class Database:

    def __init__(self):
        self.db_file = DB_FILE
        self.users = self._load_users()

    def _load_users(self):
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def add_user(self, user_id, username):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                "username": username,
                "goal": "maintain",
                "weight": 70,
                "height": 175,
                "age": 25,
                "gender": "male",
                "weight_history": [],
                "created_at": str(datetime.now())
            }
            self._save()

    def get_user(self, user_id):
        return self.users.get(str(user_id))

    def update_user(self, user_id, **kwargs):
        uid = str(user_id)

        if uid not in self.users:
            return

        for k, v in kwargs.items():
            self.users[uid][k] = v

        self._save()

    def add_weight(self, user_id, weight):
        uid = str(user_id)

        if uid in self.users:
            self.users[uid]["weight"] = weight
            self.users[uid]["weight_history"].append(weight)
            self._save()