import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router

# ============ LOGGING ============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ============ BOT SETUP ============
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Include router
dp.include_router(router)


# ============ MAIN ============
async def main():
    """Start the bot"""
    logger.info("🚀 FITNESS AI TRAINER PRO STARTED")
    logger.info(f"Bot token: {BOT_TOKEN[:10]}***")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")