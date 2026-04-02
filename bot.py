import sys
import time
import asyncio
import threading
from datetime import date, datetime
from pathlib import Path
import importlib.util
import requests
import pytz
from aiohttp import web
from PIL import Image 
from hydrogram import Client, idle, __version__
from hydrogram.raw.all import layer
import hydrogram.utils
from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium
from Lucia.Bot import SilentX
from Lucia.util.keepalive import ping_server
from Lucia.Bot.clients import initialize_clients
from logging_helper import LOGGER

botStartTime = time.time()

hydrogram.utils.MIN_CHANNEL_ID = -1009147483647

def ping_loop():
    while True:
        try:
            # 120 second ki jagah 600 second (10 min) karein
            time.sleep(600) 
            r = requests.get(URL, timeout=10)
            # Sirf fail hone par log dikhayein, success par nahi
            if r.status_code != 200:
                LOGGER.error(f"⚠️ Ping Failed: {r.status_code}")
        except:
            pass

if URL:
    threading.Thread(target=ping_loop, daemon=True).start()


def silentx_plugins_handler(app, plugins_dir: str | Path = "plugins", package_name: str = "plugins") -> list[str]:
    plugins_dir = Path(plugins_dir)
    loaded_plugins: list[str] = []

    if not plugins_dir.exists():
        LOGGER.warning("Plugins Directory '%s' Does Not Exist.", plugins_dir)
        return loaded_plugins

    for file in sorted(plugins_dir.rglob("*.py")):
import sys
import time
import asyncio
import threading
import uvloop
from datetime import date, datetime
from pathlib import Path

# Sabse pehle loop policy set karein taaki imports crash na ho
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import importlib.util
import requests
import pytz
from aiohttp import web
from PIL import Image 
from hydrogram import Client, idle, __version__
from hydrogram.raw.all import layer
import hydrogram.utils
from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium
from Lucia.Bot import SilentX
from Lucia.util.keepalive import ping_server
from Lucia.Bot.clients import initialize_clients
from logging_helper import LOGGER

botStartTime = time.time()

hydrogram.utils.MIN_CHANNEL_ID = -1009147483647

def ping_loop():
    while True:
        try:
            time.sleep(600) 
            r = requests.get(URL, timeout=10)
            if r.status_code != 200:
                LOGGER.error(f"⚠️ Ping Failed: {r.status_code}")
        except:
            pass

if URL:
    threading.Thread(target=ping_loop, daemon=True).start()

def silentx_plugins_handler(app, plugins_dir: str | Path = "plugins", package_name: str = "plugins") -> list[str]:
    plugins_dir = Path(plugins_dir)
    loaded_plugins: list[str] = []
    if not plugins_dir.exists():
        LOGGER.warning("Plugins Directory '%s' Does Not Exist.", plugins_dir)
        return loaded_plugins

    for file in sorted(plugins_dir.rglob("*.py")):
        if file.name == "__init__.py": continue
        rel_path = file.relative_to(plugins_dir).with_suffix("")
        import_path = package_name + ".".join([""] + list(rel_path.parts))
        try:
            spec = importlib.util.spec_from_file_location(import_path, file)
            if spec is None or spec.loader is None: continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            loaded_plugins.append(import_path)
            LOGGER.info("🔌 Loaded plugin: %s", import_path.removeprefix(f"{package_name}."))
        except Exception:
            LOGGER.exception("Failed To Import Plugin: %s", import_path)

    disp = getattr(app, "dispatcher", None)
    if disp:
        if 0 in disp.groups:
            all_handlers = list(disp.groups[0])
            for i, handler in enumerate(all_handlers):
                disp.remove_handler(handler, group=0)
                disp.add_handler(handler, group=i)
    return loaded_plugins

async def SilentXBotz_start():
    if MULTIPLE_DB and not DATABASE_URI2:
        LOGGER.error("DATABASE_URI2 is missing!")
        sys.exit(1)
    
    LOGGER.info("Initializing Your Bot!")
    await SilentX.start()
    
    bot_info = await SilentX.get_me()
    SilentX.username = "@" + bot_info.username
    
    await initialize_clients()
    silentx_plugins_handler(SilentX)
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS, temp.BANNED_CHATS = b_users, b_chats
        await Media.ensure_indexes()
        if MULTIPLE_DB: await Media2.ensure_indexes()
    except Exception as e:
        LOGGER.error(f"DB Error: {e}")

    temp.ME, temp.U_NAME = bot_info.id, bot_info.username
    temp.B_NAME, temp.B_LINK = bot_info.first_name, bot_info.mention
    
    asyncio.create_task(check_expired_premium(SilentX))
    LOGGER.info(f"{bot_info.first_name} started on {SilentX.username}")
    
    # Web Server Setup
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    await idle()

if __name__ == "__main__":
    try:
        # Naya loop handle karne ka sabse safe tarika
        asyncio.run(SilentXBotz_start())
    except KeyboardInterrupt:
        LOGGER.info("Service Stopped Bye 👋")
