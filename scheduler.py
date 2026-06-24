import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MORNING_MESSAGES = [
    "🌅 Доброе утро! Сегодня отличный день для тренировки. Не забудь позавтракать! 💪",
    "☀️ Новый день — новые возможности! Выпей стакан воды и начни день с разминки! 🏃",
    "🔥 Привет! Помни: каждая тренировка приближает тебя к цели. Вперёд! 💯",
    "🌄 Доброе утро! Сегодня не забудь записать свой вес и калории. Прогресс = результат! 📊",
]

EVENING_MESSAGES = [
    "🌙 Как прошёл день? Не забудь записать тренировку командой /workout 💪",
    "⭐ Вечер! Запиши калории за сегодня: /cal [число]. Это помогает отслеживать прогресс!",
    "🌙 Время отдыха! Помни: сон 7-9 часов — это когда растут мышцы. Спокойной ночи! 😴",
]

_scheduler_running = False


def setup_scheduler(bot):
    asyncio.create_task(_run_scheduler(bot))


async def _run_scheduler(bot):
    global _scheduler_running
    if _scheduler_running:
        return
    _scheduler_running = True

    import random
    sent_morning = set()
    sent_evening = set()

    while True:
        try:
            now = datetime.now()
            hour = now.hour
            day_key = now.strftime('%Y-%m-%d')

            if hour == 8 and day_key not in sent_morning:
                sent_morning.add(day_key)
                await _send_broadcast(bot, random.choice(MORNING_MESSAGES))

            if hour == 20 and day_key not in sent_evening:
                sent_evening.add(day_key)
                await _send_broadcast(bot, random.choice(EVENING_MESSAGES))

            if len(sent_morning) > 10:
                sent_morning = set(list(sent_morning)[-5:])
            if len(sent_evening) > 10:
                sent_evening = set(list(sent_evening)[-5:])

        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        await asyncio.sleep(3600)


async def _send_broadcast(bot, text: str):
    try:
        from database import Database
        db = Database()
        uids = db.get_users_with_notifications()
        sent = 0
        for uid in uids:
            try:
                await bot.send_message(uid, text)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
        logger.info(f"Broadcast sent to {sent}/{len(uids)} users")
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
