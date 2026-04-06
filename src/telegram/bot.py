"""
TelegramBot - Listens for messages via polling and pushes to MessageQueue
"""
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)
from config.settings import Config
from src.core.message_queue import MessageQueue, IncomingMessage

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, config: Config, queue: MessageQueue):
        self.config = config
        self.queue = queue
        self.app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("help", self._handle_help))
        # Catch all text messages (not commands)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hi! I'm StormClaw, you personal AI assistant. How can I help you?"
        )

    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Send me any message and I'll reply to you."
        )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        chat_id = msg.chat_id

        if self.config.ALLOWED_CHAT_IDS and chat_id not in self.config.ALLOWED_CHAT_IDS:
            logger.warning(f"Blocked message from unauthorized chat_id={chat_id}")
            await msg.reply_text("You are not authorized.")
            return

        incoming = IncomingMessage(
            chat_id=chat_id,
            user_id=msg.from_user.id,
            username=msg.from_user.username or str(msg.from_user.id),
            text=msg.text,
            message_id=msg.message_id,
        )

        logger.info(f"Received: {incoming}")
        await self.queue.put(incoming)

        await msg.reply_text("Looking for the best answer...")

    async def send_message(self, chat_id: int, text: str):
        await self.app.bot.send_message(chat_id=chat_id, text=text)

    # ------------------------------------------------------------------
    # Start polling (runs forever)
    # ------------------------------------------------------------------

    async def listen(self):
        logger.info("Telegram bot starting polling...")
        async with self.app:
            await self.app.start()
            await self.app.updater.start_polling(drop_pending_updates=True)
            # Keep alive — the event loop handles the rest
            await asyncio.Event().wait()  # block until cancelled
            await self.app.updater.stop()
            await self.app.stop()


import asyncio
