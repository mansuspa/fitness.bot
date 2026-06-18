import json
import logging
from datetime import datetime
from config import DB_FILE

logger = logging.getLogger(__name__)


class Database:
    """Database manager for fitness bot"""
    
    @staticmethod
    def load():
        """Load users database"""
        if not __import__("os").path.exists(DB_FILE):
            return {}
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"DB LOAD ERROR: {e}")
            return {}
    
    @staticmethod
    def save(data):
        """Save users database"""
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"DB SAVE ERROR: {e}")
    
    @staticmethod
    def get_or_create_user(uid: str, name: str, data: dict) -> dict:
        """Get or create user profile"""
        if uid not in data:
            data[uid] = {
                "name": name,
                "goal": None,
                "premium": False,
                "created_at": datetime.now().isoformat(),
                "stats": {
                    "weight": None,
                    "height": None,
                    "age": None,
                    "gender": None
                },
                "workouts": [],
                "daily_calories": None,
                "active": True
            }
            Database.save(data)
        return data[uid]
    
    @staticmethod
    def update_user(uid: str, user_data: dict, data: dict):
        """Update user profile"""
        if uid in data:
            data[uid].update(user_data)
            Database.save(data)
    
    @staticmethod
    def add_workout(uid: str, workout: dict, data: dict):
        """Add workout record"""
        if uid in data:
            if "workouts" not in data[uid]:
                data[uid]["workouts"] = []
            workout["date"] = datetime.now().isoformat()
            data[uid]["workouts"].append(workout)
            Database.save(data)
    
    @staticmethod
    def get_user_stats(uid: str, data: dict) -> dict:
        """Get user statistics"""
        if uid not in data:
            return {}
        
        user = data[uid]
        workouts = user.get("workouts", [])
        
        return {
            "total_workouts": len(workouts),
            "goal": user.get("goal"),
            "premium": user.get("premium"),
            "stats": user.get("stats"),
            "daily_calories": user.get("daily_calories")
        }