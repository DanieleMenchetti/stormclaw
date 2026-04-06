import asyncio
import logging
import os
from src.core.service import BackgroundService
from config.settings import Config

async def main():
    if not os.path.exists(Config.LOG_PATH):
        os.makedirs(Config.LOG_PATH)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/app.log"),
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting Telegram AI Agent Service...")
    service = BackgroundService()
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
