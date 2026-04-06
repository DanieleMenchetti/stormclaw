"""
AIAgent - Consumes messages from queue and processes them.
"""
import asyncio
import logging
from agno.agent import Agent
from agno.models.ollama import Ollama
from config.settings import Config
from src.core.message_queue import MessageQueue, IncomingMessage

logger = logging.getLogger(__name__)


class AIAgent:
    """
    AI Agent based onAgno framework
    """

    SYSTEM_PROMPT = """
    You are an AI Agent called StormClaw. 
    
    You have to assist the user.
    """

    def __init__(self, config: Config, queue: MessageQueue, bot):
        self.config = config
        self.queue = queue
        self.bot = bot
        self._agent = Agent(
            model=Ollama(id=config.OLLAMA_MODEL),
            description=self.SYSTEM_PROMPT,
            markdown=False,
        )
        self._sessions: dict[int, list[dict]] = {}

    async def run(self):
        logger.info("AI Agent worker started...")
        while True:
            message = await self.queue.get()
            try:
                await self._process(message)
            except Exception as e:
                logger.exception(f"Error processing {message}: {e}")
                await self.bot.send_message(
                    message.chat_id,
                    "Si è verificato un errore durante l'elaborazione."
                )
            finally:
                self.queue.task_done()

    async def _process(self, message: IncomingMessage):
        logger.info(f"Processing: {message}")

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._agent.run(
                message.text,
                session_id=str(message.chat_id),
            )
        )

        response_text = response.content if response.content else "Nessuna risposta."
        await self.bot.send_message(message.chat_id, response_text)
        logger.info(f"Replied to chat_id={message.chat_id}")