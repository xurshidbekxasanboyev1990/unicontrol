import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database import init_db
from bot.handlers import routers
from bot.middlewares import (
    ThrottlingMiddleware,
    ForceSubscribeMiddleware,
    MaintenanceModeMiddleware,
    UserTrackingMiddleware,
    BannedUserMiddleware
)
from bot.scheduler import AttendanceNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, notifier: AttendanceNotifier):
    """Actions to perform on bot startup"""
    logger.info("Bot starting up...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Start attendance notifier
    await notifier.start()
    logger.info("Attendance notifier started")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")


async def on_shutdown(bot: Bot, notifier: AttendanceNotifier):
    """Actions to perform on bot shutdown"""
    logger.info("Bot shutting down...")
    
    # Stop notifier
    await notifier.stop()
    
    # Close bot session
    await bot.session.close()
    
    logger.info("Bot stopped")


async def main():
    """Main entry point"""
    # Validate settings
    if not settings.bot_token or settings.bot_token == "your_bot_token_here":
        logger.error("BOT_TOKEN is not set! Please configure .env file.")
        sys.exit(1)
    
    # Create bot instance
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher with memory storage
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middlewares (order matters!)
    # 1. User tracking - always track users
    dp.message.middleware(UserTrackingMiddleware())
    dp.callback_query.middleware(UserTrackingMiddleware())
    
    # 2. Banned user check
    dp.message.middleware(BannedUserMiddleware())
    dp.callback_query.middleware(BannedUserMiddleware())
    
    # 3. Maintenance mode check
    dp.message.middleware(MaintenanceModeMiddleware())
    dp.callback_query.middleware(MaintenanceModeMiddleware())
    
    # 4. Force subscribe check
    dp.message.middleware(ForceSubscribeMiddleware(bot))
    dp.callback_query.middleware(ForceSubscribeMiddleware(bot))
    
    # 5. Throttling
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    # Register all routers
    for router in routers:
        dp.include_router(router)
    
    # Create attendance notifier
    notifier = AttendanceNotifier(bot)
    
    # Initialize database before polling
    await init_db()
    logger.info("Database initialized")
    
    # Start attendance notifier
    await notifier.start()
    logger.info("Attendance notifier started")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")
    
    try:
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
    finally:
        # Stop notifier
        await notifier.stop()
        # Close bot session
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
