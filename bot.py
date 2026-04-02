import sys
import time
import asyncio
import threading
import uvloop
from datetime import date, datetime
from pathlib import Path

# --- LOOP POLICY SETUP (CRITICAL FOR RENDER/HYDROGRAM) ---
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

# Channel ID range fix
hydrogram.utils.MIN_CHANNEL_ID = -1009147483647

def ping_loop():
    while True:
        try:
            time.sleep(600) 
            r = requests.get(URL, timeout=10)
            if r.status_code != 200:
                LOGGER.error(f"⚠️ Ping Failed: {r.status_code}")
        except Exception:
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
        if file.name == "__init__.py":
            continue
            
        rel_path = file.relative_to(plugins_dir).with_suffix("")
        import_path = package_name + ".".join([""] + list(rel_path.parts))
        
        try:
            spec = importlib.util.spec_from_file_location(import_path, file)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            loaded_plugins.append(import_path)
            LOGGER.info("🔌 Loaded plugin: %s", import_path.removeprefix(f"{package_name}."))
        except Exception:
            LOGGER.exception("Failed To Import Plugin: %s", import_path)

    disp = getattr(app, "dispatcher", None)
    if disp and 0 in disp.groups:
        all_handlers = list(disp.groups[0])
        for i, handler in enumerate(all_handlers):
            disp.remove_handler(handler, group=0)
            disp.add_handler(handler, group=i)
            
    return loaded_plugins

async def SilentXBotz_start():
    if MULTIPLE_DB and not DATABASE_URI2:
        LOGGER.error("DATABASE_URI2 is missing but MULTIPLE_DB is True!")
        sys.exit(1)
    
    LOGGER.info("Initializing Your Bot...")
    await SilentX.start()
    
    # User info load karna zaroori hai message bhejte waqt
    me = await SilentX.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    SilentX.username = "@" + me.username
    
    await initialize_clients()
    silentx_plugins_handler(SilentX)
    
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS, temp.BANNED_CHATS = b_users, b_chats
        await Media.ensure_indexes()
        if MULTIPLE_DB:
            await Media2.ensure_indexes()
    except Exception as e:
        LOGGER.error(f"DB Error: {e}")

    # --- RESTART LOG LOGIC ---
    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")
    
    if LOG_CHANNEL:
        try:
            await SilentX.send_message(
                chat_id=LOG_CHANNEL,
                text=script.RESTART_TXT.format(temp.B_LINK, today, time_str)
            )
            LOGGER.info("✅ Restart message sent to Log Channel.")
        except Exception as e:
            LOGGER.error(f"❌ Failed to send restart log: {e}")

    asyncio.create_task(check_expired_premium(SilentX))
    LOGGER.info(f"✅ {me.first_name} is online on {SilentX.username}!")
    
    # --- WEB SERVER FOR RENDER (PORT BINDING) ---
    try:
        web_app = await web_server()
        app_runner = web.AppRunner(web_app)
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()
        LOGGER.info(f"🌐 Web Server is running on Port {PORT}")
    except Exception as e:
        LOGGER.warning(f"⚠️ Web Server failed: {e}")

    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(SilentXBotz_start())
    except KeyboardInterrupt:
        LOGGER.info("Service Stopped Bye 👋")
