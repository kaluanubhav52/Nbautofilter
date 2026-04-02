import sys
import logging
import time
import asyncio
import threading
import uvloop
from datetime import date, datetime
from pathlib import Path

# --- STEP 1: LOGGING CONTROL (Render fix for "Output Too Large") ---
# Logging ko WARNING par set kiya hai taaki faltu ki details load na hon
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Kurigram aur aiohttp ke internal logs ko silent karein
logging.getLogger("kurigram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

# Loop Policy Setup
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import importlib.util
import requests
import pytz
from aiohttp import web
from PIL import Image 
from kurigram import Client, idle, __version__
from kurigram.raw.all import layer
import kurigram.utils
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
kurigram.utils.MIN_CHANNEL_ID = -1009147483647

def ping_loop():
    while True:
        try:
            time.sleep(600) 
            r = requests.get(URL, timeout=10)
            if r.status_code != 200:
                LOGGER.error(f"⚠️ Ping Failed: {r.status_code}")
        except: pass

if URL:
    threading.Thread(target=ping_loop, daemon=True).start()

def silentx_plugins_handler(app, plugins_dir: str | Path = "plugins", package_name: str = "plugins") -> list[str]:
    plugins_dir = Path(plugins_dir)
    loaded_plugins = []
    if not plugins_dir.exists(): return loaded_plugins

    for file in sorted(plugins_dir.rglob("*.py")):
        if file.name == "__init__.py": continue
        rel_path = file.relative_to(plugins_dir).with_suffix("")
        import_path = package_name + ".".join([""] + list(rel_path.parts))
        try:
            spec = importlib.util.spec_from_file_location(import_path, file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[import_path] = module
                loaded_plugins.append(import_path)
                # Sirf ERROR level par print hoga agar kuch bada issue ho
        except Exception:
            LOGGER.error(f"Plugin Error: {import_path}")
    return loaded_plugins

async def SilentXBotz_start():
    if MULTIPLE_DB and not DATABASE_URI2:
        sys.exit(1)
    
    LOGGER.warning("🚀 Starting SilentXBotz on Kurigram...")
    await SilentX.start()
    
    me = await SilentX.get_me()
    temp.ME, temp.U_NAME = me.id, me.username
    temp.B_NAME, temp.B_LINK = me.first_name, me.mention
    SilentX.username = "@" + me.username
    
    await initialize_clients()
    silentx_plugins_handler(SilentX)
    
    if ON_HEROKU: asyncio.create_task(ping_server())

    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS, temp.BANNED_CHATS = b_users, b_chats
        await Media.ensure_indexes()
        if MULTIPLE_DB: await Media2.ensure_indexes()
    except: pass

    # Restart Log (Timing fix with IST)
    tz = pytz.timezone("Asia/Kolkata")
    time_str = datetime.now(tz).strftime("%H:%M:%S %p")
    if LOG_CHANNEL:
        try:
            await SilentX.send_message(LOG_CHANNEL, script.RESTART_TXT.format(temp.B_LINK, date.today(), time_str))
        except: pass

    asyncio.create_task(check_expired_premium(SilentX))
    LOGGER.warning(f"✅ {me.first_name} Started Successfully!")
    
    # Web Server for Render Port Binding
    try:
        web_app = await web_server()
        app_runner = web.AppRunner(web_app)
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()
    except: pass

    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(SilentXBotz_start())
    except (KeyboardInterrupt, SystemExit):
        pass
