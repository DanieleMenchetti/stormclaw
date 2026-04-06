"""
MessageQueue - async queue between Telegram receiver and AI agent
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IncomingMessage:
    chat_id: int
    user_id: int
    username: str
    text: str
    message_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<Msg from @{self.username} [{self.chat_id}]: {self.text[:60]}>"


class MessageQueue:
    def __init__(self, maxsize: int = 100):
        self._queue: asyncio.Queue[IncomingMessage] = asyncio.Queue(maxsize=maxsize)

    async def put(self, message: IncomingMessage):
        await self._queue.put(message)

    async def get(self) -> IncomingMessage:
        return await self._queue.get()

    def task_done(self):
        self._queue.task_done()

    def qsize(self):
        return self._queue.qsize()
