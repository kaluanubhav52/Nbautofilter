from datetime import timedelta
import pytz
import io, segno, random
import datetime, time
from Script import script 
from info import *
from utils import get_seconds, temp
from database.users_chats_db import db 
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import ForceReply, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.types import *
from logging_helper import LOGGER

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        if await db.remove_premium_access(user_id):
            await message.reply_text("ᴜꜱᴇʀ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !")
            await client.send_message(
                chat_id=user_id,
                text=f"<b>ʜᴇʏ {user.mention},\n\n𝒀𝒐𝒖𝒓 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑨𝒄𝒄𝒆𝒔𝒔 𝑯𝒂𝒔 𝑩𝒆𝒆𝒏 𝑹𝒆𝒎𝒐𝒗𝒆𝒅. 𝑻𝒉𝒂𝒏𝒌 𝒀𝒐𝒖 𝑭𝒐𝒓 𝑼𝒔𝒊𝒏𝒈 𝑶𝒖𝒓 𝑺𝒆𝒓𝒗𝒊𝒄𝒆 😊. 𝑪𝒍𝒊𝒄𝒌 𝑶𝒏 /plan 𝑻𝒐 𝑪𝒉𝒆𝒄𝒌 𝑶𝒖𝒓 𝑶𝒕𝒉𝒆𝒓 𝑷𝒍𝒂𝒏𝒔.\n\n<blockquote>आपका Premium Access हटा दिया गया है। हमारी सेवा का उपयोग करने के लिए धन्यवाद 🥳 हमारी अन्य योजनाओं की जाँच करने के लिए /plan पर क्लिक करें ।</blockquote></b>"
            )
        else:
            await message.reply_text("ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜꜱᴇᴅ !\nᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ, ɪᴛ ᴡᴀꜱ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ɪᴅ ?")
    else:
        await message.reply_text("ᴜꜱᴀɢᴇ : /remove_premium user_id") 

@Client.on_message(filters.command("myplan"))
async def myplan(client, message):
    try:
        user = message.from_user.mention 
        user_id = message.from_user.id
        data = await db.get_user(message.from_user.id) 
        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time") 
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")            
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left_str = f"{days} ᴅᴀʏꜱ, {hours} ʜᴏᴜʀꜱ, {minutes} ᴍɪɴᴜᴛᴇꜱ"
            await message.reply_text(f"⚜️ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴅᴀᴛᴀ :\n\n👤 ᴜꜱᴇʀ : {user}\n⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}")   
        else:
            await message.reply_text(f"<b>ʜᴇʏ {user},\n\nʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ. ʙᴜʏ ᴏᴜʀ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ.</b>",
	    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ •", callback_data='buy')]]))
    except Exception as e:
        LOGGER.info(e)

@Client.on_message(filters.command("get_premium") & filters.user(ADMINS))
async def get_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        data = await db.get_user(user_id)  
        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time") 
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")            
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(f"⚜️ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴅᴀᴛᴀ :\n\n👤 ᴜꜱᴇʀ : {user.mention}\n⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}")
        else:
            await message.reply_text("ɴᴏ ᴀɴʏ ᴘʀᴇᴍɪᴜᴍ ᴅᴀᴛᴀ ᴏꜰ ᴛʜᴇ ᴡᴀꜱ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ !")
    else:
        await message.reply_text("ᴜꜱᴀɢᴇ : /get_premium user_id")

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def give_premium_cmd_handler(client, message):
    if len(message.command) == 4:
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : %I:%M:%S %p") 
        user_id = int(message.command[1])  
        user = await client.get_users(user_id)
        time = message.command[2]+" "+message.command[3]
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time}  
            await db.update_user(user_data) 
            data = await db.get_user(user_id)
            expiry = data.get("expiry_time")   
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")         
            await message.reply_text(f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅\n\n👤 ᴜꜱᴇʀ : {user.mention}\n⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time}</code>\n\n⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}", disable_web_page_preview=True)
            await client.send_message(
                chat_id=user_id,
                text=f"👋 ʜᴇʏ {user.mention},\nᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴘᴜʀᴄʜᴀꜱɪɴɢ ᴘʀᴇᴍɪᴜᴍ.\nᴇɴᴊᴏʏ !! ✨🎉\n\n⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time}</code>\n⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}", disable_web_page_preview=True              
            )    
            await client.send_message(PREMIUM_LOGS, text=f"#Added_Premium\n\n👤 ᴜꜱᴇʀ : {user.mention}\n⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time}</code>\n\n⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}", disable_web_page_preview=True)
                    
        else:
            await message.reply_text("Invalid time format. Please use '1 day for days', '1 hour for hours', or '1 min for minutes', or '1 month for months' or '1 year for year'")
    else:
        await message.reply_text("Usage : /add_premium user_id time (e.g., '1 day for days', '1 hour for hours', or '1 min for minutes', or '1 month for months' or '1 year for year')")

@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_user(client, message):
    aa = await message.reply_text("<i>ꜰᴇᴛᴄʜɪɴɢ...</i>")
    new = f" ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ʟɪꜱᴛ :\n\n"
    user_count = 1
    users = await db.get_all_users()
    async for user in users:
        data = await db.get_user(user['id'])
        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time") 
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")            
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"	 
            new += f"{user_count}. {(await client.get_users(user['id'])).mention}\n👤 ᴜꜱᴇʀ ɪᴅ : {user['id']}\n⏳ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str_in_ist}\n⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n"
            user_count += 1
        else:
            pass
    try:    
        await aa.edit_text(new)
    except MessageTooLong:
        with open('usersplan.txt', 'w+') as outfile:
            outfile.write(new)
        await message.reply_document('usersplan.txt', caption="Paid Users:")



# --- 1. /plan Command (Main Menu) ---
@Client.on_message(filters.command("plan") & filters.private)
async def plan_handler(client, message):
    user_id = message.from_user.id 
    
    # Admin Alert (Optional)
    await client.send_message(PREMIUM_LOGS, f"👤 {message.from_user.mention} (`{user_id}`) is checking /plan")

    btn = [[
        InlineKeyboardButton('• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •', callback_data='buy_info'),           
    ],[                
        InlineKeyboardButton('• ʀᴇꜰᴇʀ ꜰʀɪᴇɴᴅꜱ', callback_data='reffff'),                
        InlineKeyboardButton('ꜰʀᴇᴇ ᴛʀɪᴀʟ •', callback_data='give_trial')        
    ],[            
        InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ 🚫', callback_data='close_data')
    ]]
    
    await message.reply_photo(
        photo=random.choice(PICS), 
        caption=script.BPREMIUM_TXT, 
        reply_markup=InlineKeyboardMarkup(btn)
    )

# --- 2. Buy Info (Automatic Buttons from Config) ---
@Client.on_callback_query(filters.regex("buy_info"))
async def buy_info_handler(client, query):
    # Buttons config.py ke PREMIUM_PLANS se apne aap banenge
    btn = [[InlineKeyboardButton(f"✨ {t} - ₹{p}", callback_data=f"gen_qr_{p}")] 
           for p, t in PREMIUM_PLANS.items()]
    btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="premium")])
    
    await query.message.edit_caption(
        caption=script.PREMIUM_TEXT.format(query.from_user.mention),
        reply_markup=InlineKeyboardMarkup(btn)
    )

# --- 3. QR Generation Logic ---
@Client.on_callback_query(filters.regex(r"gen_qr_(\d+)"))
async def gen_qr_handler(client, query):
    amount = int(query.matches[0].group(1))
    upi_url = f"upi://pay?pa={UPI_ID}&pn={RECEIVER_NAME}&am={amount}&cu=INR"
    
    qr_img = segno.make(upi_url)
    out = io.BytesIO()
    qr_img.save(out, kind='png', scale=10)
    out.seek(0)
    
    btn = [[InlineKeyboardButton('✅ I Have Paid', callback_data=f"paid_{amount}")],
           [InlineKeyboardButton('⇋ Back ⇋', callback_data='buy_info')]]
    
    await query.message.edit_media(
        media=InputMediaPhoto(media=out, caption=script.QR_TEXT.format(amount, UPI_ID)),
        reply_markup=InlineKeyboardMarkup(btn)
    )

# --- 4. I Have Paid (UTR Request) ---
@Client.on_callback_query(filters.regex(r"paid_(\d+)"))
async def paid_handler(client, query):
    await query.message.reply_text(
        text=script.ASK_UTR_TEXT,
        reply_markup=ForceReply(selective=True)
    )
    await query.answer()

# --- 5. [CRITICAL] /cancel Command ---
# Iska group humne -1 rakha hai taaki ye search se pehle trigger ho
@Client.on_message(filters.command("cancel") & filters.private, group=-1)
async def cancel_handler(client, message):
    await message.reply_text(
        text=script.CANCEL_TEXT,
        reply_markup=ReplyKeyboardRemove()
    )
    # Ye line zaroori hai taaki niche wale filters trigger na hon
    message.stop_propagation()

# --- 6. UTR Submission & 12-Digit Check ---
# Group ko -2 rakha hai (High Priority)
@Client.on_message(filters.private & filters.text & filters.reply, group=-2)
async def handle_utr_submission(client, message):
    # Check if reply is to UTR request
    if message.reply_to_message and "Step 2: Verification" in message.reply_to_message.text:
        utr_id = message.text.strip()
        
        # Validation
        if not (utr_id.isdigit() and len(utr_id) == 12):
            await message.reply_text(
                text=script.INVALID_UTR_TEXT,
                reply_markup=ForceReply(selective=True)
            )
            # Stop propagation yahan bhi zaroori hai taaki galat ID par bhi search na ho
            message.stop_propagation()
            return

        # Admin Logs
        user_id = message.from_user.id
        await client.send_message(
            chat_id=PREMIUM_LOGS,
            text=f"<b>💰 New Payment Alert</b>\n\n👤 User: {message.from_user.mention}\n🆔 ID: <code>{user_id}</code>\n🔢 UTR: <code>{utr_id}</code>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Approve", callback_data=f"add_p_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"rej_p_{user_id}")
            ]])
        )
        await message.reply_text(script.SUBMITTED_TEXT, reply_markup=ReplyKeyboardRemove())
        
        # [VERY IMPORTANT] Iske baad bot kuch aur nahi karega (Search Stop)
        message.stop_propagation()

# --- 7. Admin Actions: Approve & Reject Handler ---

@Client.on_callback_query(filters.regex(r"^(add_p|rej_p)_(\d+)"))
async def admin_approval_callback(client, query):
    # Action: add_p ya rej_p | User_ID: (\d+)
    action = query.data.split("_")[0] 
    user_id = int(query.data.split("_")[2]) 
    admin_name = query.from_user.mention

    if action == "add":
        # Aapne kaha tha expiry pehle se set hai, 
        # Toh bas user ko active karne ka message aur database update:
        expiry_days = 30 # Default 30, ya plans ke hisaab se change karein
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=expiry_days)
        
        try:
            # Database update (Aapka existing method use karein)
            await db.update_user({"id": user_id, "expiry_time": expiry_date})
            
            # User ko notify karein
            await client.send_message(
                chat_id=user_id,
                text=f"<b>🎉 ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n\nAapka payment verify ho gaya hai.\n⏳ ᴠᴀʟɪᴅɪᴛʏ: {expiry_days} Days\n📅 ᴇxᴘɪʀʏ: {expiry_date.strftime('%d-%m-%Y')}"
            )
            
            # Admin log update karein
            await query.message.edit_text(
                f"✅ <b>Approved By:</b> {admin_name}\n👤 <b>User:</b> <code>{user_id}</code>\n📅 <b>Expiry:</b> {expiry_date.strftime('%d-%m-%Y')}"
            )
            await query.answer("User Approved!", show_alert=True)
            
        except Exception as e:
            await query.answer(f"Database Error: {e}", show_alert=True)

    elif action == "rej":
        try:
            await client.send_message(
                chat_id=user_id,
                text=f"<b>❌ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴊᴇᴄᴛᴇᴅ!</b>\n\nAapka UTR verify nahi ho paya. Sahi details ke saath dobara try karein ya @{ADMIN_USER} se contact karein."
            )
            await query.message.edit_text(f"❌ <b>Rejected By:</b> {admin_name}\n👤 <b>User:</b> <code>{user_id}</code>")
            await query.answer("User Rejected!", show_alert=True)
        except Exception as e:
            await query.answer(f"Error: {e}", show_alert=True)
