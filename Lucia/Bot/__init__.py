import asyncio
import uvloop
from hydrogram import Client
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from hydrogram import types
from aiohttp import web
from logging_helper import LOGGER

# --- Loop Fix Start ---
# Ye lines initialize hone se pehle loop setup kar dengi
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# --- Loop Fix End ---

class SilentXBot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
      
# Ab ye error nahi dega kyunki upar loop set ho chuka hai
SilentX = SilentXBot()

multi_clients = {}
work_loads = {}
