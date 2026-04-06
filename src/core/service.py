"""
BackgroundService - Orchestrates Telegram listener + AI Agent
"""
import asyncio
import logging
from config.settings import config
from src.telegram.bot import TelegramBot
from src.agent.ai_agent import AIAgent
from src.core.message_queue import MessageQueue

logger = logging.getLogger(__name__)


class BackgroundService:
    """
    Main service that wires together:
      1. TelegramBot  → receives messages and pushes to queue
      2. MessageQueue → decouples I/O from processing
      3. AIAgent      → consumes queue, processes with AI, replies
    """

    def __init__(self):
        config.validate()
        self.queue = MessageQueue()
        self.bot = TelegramBot(config, self.queue)
        self.agent = AIAgent(config, self.queue, self.bot)

    async def start(self):
        logger.info("Service starting — launching tasks...")
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.bot.listen(), name="telegram-listener")
            tg.create_task(self.agent.run(), name="ai-agent-worker")
