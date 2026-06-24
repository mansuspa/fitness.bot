import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import register_all_handlers
from scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def flush_old_sessions(bot: Bot):
    """
    Сбрасывает старые long-polling сессии Telegram.
    Вызывает getUpdates с timeout=0 несколько раз чтобы
    Telegram закрыл все старые соединения.
    """
    logger.info("Flushing old Telegram sessions...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"delete_webhook: {e}")

    # Несколько попыток getUpdates с timeout=0 чтобы перехватить сессию
    offset = None
    for attempt in range(5):
        try:
            updates = await bot.get_updates(
                offset=offset,
                limit=1,
                timeout=0,
                allowed_updates=[]
            )
            if updates:
                offset = updates[-1].update_id + 1
            logger.info(f"Session flush attempt {attempt + 1}/5: OK")
        except Exception as e:
            logger.info(f"Session flush attempt {attempt + 1}/5: {e}")
        await asyncio.sleep(2)


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    register_all_handlers(dp)
    setup_scheduler(bot)

    print("🔥 FITNESS AI V11 PRO STARTED")

    await flush_old_sessions(bot)

    logger.info("Starting polling (clean session)...")

    try:
        await dp.start_polling(
            bot,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "pre_checkout_query"],
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
