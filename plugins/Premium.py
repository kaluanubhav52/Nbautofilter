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

# --- [ SECTION 2: PAYMENT & QR LOGIC ] ---

@Client.on_callback_query(filters.regex(r"buy_info"))
async def buy_info_handler(client, query):
    btn = [[InlineKeyboardButton(f"✨ {t} - ₹{p}", callback_data=f"gen_qr_{p}")] for p, t in PREMIUM_PLANS.items()]
    btn.append([InlineKeyboardButton('⇋ Back ⇋', callback_data='premium')])
    await query.message.edit_caption(caption=script.PREMIUM_TEXT, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"gen_qr_\d+"))
async def gen_qr_callback(client, query):
    amount = int(query.data.split("_")[2])
    upi_url = f"upi://pay?pa={UPI_ID}&pn={RECEIVER_NAME}&am={amount}&cu=INR"
    
    qr_img = segno.make(upi_url); out = io.BytesIO(); qr_img.save(out, kind='png', scale=10); out.seek(0)
    btn = [[InlineKeyboardButton('✅ I have Paid✅', callback_data=f"sub_id_{amount}")],
           [InlineKeyboardButton('⇋ Back ⇋', callback_data='buy_info')]]
    
    await query.message.edit_media(media=InputMediaPhoto(media=out, caption=f"<b>✅ Scan & Pay ₹{amount}</b>\n\nUPI: <code>{UPI_ID}</code>"), reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"sub_id_\d+"))
async def ask_id(client, query):
    amount = query.data.split("_")[2]
    await query.message.reply_text(f"<b>📩 Submit Transaction ID (₹{amount})</b>\n\n12-digit UPI ID yahan reply karein.", reply_markup=ForceReply(selective=True))

@Client.on_message(filters.private & filters.text & filters.reply, group=1)
async def handle_id_submission(client, message):
    # Check karein ki kya ye wahi message hai jisme UTR maanga gaya tha
    if message.reply_to_message and "Submit Transaction ID" in message.reply_to_message.text:
        txn_id = message.text.strip()
        user_id = message.from_user.id
        
        # Admin Logs mein notification (Buttons ke saath)
        await client.send_message(
            chat_id=PREMIUM_LOGS, 
            text=f"<b>💰 New Payment Alert</b>\n\n"
                 f"👤 <b>User:</b> {message.from_user.mention}\n"
                 f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
                 f"🔢 <b>TXN ID:</b> <code>{txn_id}</code>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"add_p_{user_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"rej_p_{user_id}")
                ]
            ])
        )
        
        await message.reply_text("✅ <b>Transaction ID received!</b>\nAdmin verify karke aapko notify karenge. Tab tak intezar karein.")
        
        # 🔥 Sabse Important: Isse bot aage search nahi karega
        message.stop_propagation()

# --- [ ADMIN ACTIONS: APPROVE & REJECT ] ---

@Client.on_callback_query(filters.regex(r"add_p_\d+"))
async def approve_payment_handler(client, query):
    user_id = int(query.data.split("_")[2])
    
    # 1 Month (30 Days) calculation
    seconds = await get_seconds("30 days")
    expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    
    # Database Update
    await db.update_user({"id": user_id, "expiry_time": expiry_time})
    
    # User ko Message bhejna
    try:
        await client.send_message(
            chat_id=user_id,
            text="<b>🎉 Congratulations!</b>\n\nAapka Payment verify ho gaya hai. Aapka <b>Premium Plan (1 Month)</b> activate kar diya gaya hai. Enjoy! ✨"
        )
    except Exception as e:
        print(f"User Notify Error: {e}")

    # Admin Log Update
    await query.message.edit_text(f"✅ <b>Approved!</b>\nUser ID: <code>{user_id}</code>\nStatus: Premium Activated (30 Days)")
    await query.answer("User Approved Successfully!", show_alert=True)


@Client.on_callback_query(filters.regex(r"rej_p_\d+"))
async def reject_payment_handler(client, query):
    user_id = int(query.data.split("_")[2])
    
    # User ko Reject ka Message bhejna
    try:
        await client.send_message(
            chat_id=user_id,
            text="<b>❌ Payment Rejected!</b>\n\nAapki bheji gayi Transaction ID verify nahi ho payi hai. Agar aapne sahi payment ki hai, toh please Admin @{} se contact karein.".format(ADMIN_USER)
        )
    except Exception as e:
        print(f"User Notify Error: {e}")

    # Admin Log Update
    await query.message.edit_text(f"❌ <b>Rejected!</b>\nUser ID: <code>{user_id}</code>\nStatus: Payment Declined")
    await query.answer("User Rejected!", show_alert=True)
