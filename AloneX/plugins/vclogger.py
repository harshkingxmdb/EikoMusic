import asyncio
import logging
from typing import Set, Dict

from pyrogram import filters
from pyrogram.types import Message
from pytgcalls import filters as fl
from pytgcalls.types import GroupCallParticipant, UpdatedGroupCallParticipant

from AloneX import app, anon

logger = logging.getLogger(__name__)

enabled_chats: Set[int] = set()
user_join_count: Dict[tuple, int] = {}
user_cache: Dict[int, tuple] = {}
DELETE_DELAY = 7


async def delete_message_after_delay(chat_id: int, message_id: int):
    try:
        await asyncio.sleep(DELETE_DELAY)
        await app.delete_messages(chat_id, message_id)
    except Exception:
        pass


async def get_user_info(chat_id: int, user_id: int) -> tuple:
    if user_id in user_cache:
        return user_cache[user_id]

    name = None
    username = "Iɢɴᴏʀᴇᴅ"

    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member and member.user:
            user = member.user
            name = user.first_name or ""
            if user.last_name:
                name += f" {user.last_name}"
            username = f"@{user.username}" if user.username else "Iɢɴᴏʀᴇᴅ"
    except Exception:
        pass

    user_cache[user_id] = (name, username)
    return name, username


async def send_join_notification(chat_id: int, user_id: int):
    key = (chat_id, user_id)
    user_join_count[key] = user_join_count.get(key, 0) + 1
    count = user_join_count[key]

    name, username = await get_user_info(chat_id, user_id)
    mention = f'<a href="tg://user?id={user_id}">{name or "User"}</a>'

    text = (
        "<b>#JoinVideoChat</b>\n\n"
        f"<b>● ɴᴀᴍᴇ ➛</b> {mention}\n"
        f"<b>● ɪᴅ ➛</b> <code>{user_id}</code>\n"
        f"<b>● ᴜsᴇʀɴᴀᴍᴇ ➛</b> {username}"
    )

    if count > 1:
        text += f"\n\n<b>🔁 ᴊᴏɪɴ ᴄᴏᴜɴᴛ ➛</b> <code>{count}</code>"

    msg = await app.send_message(chat_id, text)
    asyncio.create_task(delete_message_after_delay(chat_id, msg.id))


async def send_leave_notification(chat_id: int, user_id: int):
    name, username = await get_user_info(chat_id, user_id)
    mention = f'<a href="tg://user?id={user_id}">{name or "User"}</a>'

    text = (
        "<b>#LeaveVideoChat</b>\n\n"
        f"<b>● ɴᴀᴍᴇ ➛</b> {mention}\n"
        f"<b>● ɪᴅ ➛</b> <code>{user_id}</code>\n"
        f"<b>● ᴜsᴇʀɴᴀᴍᴇ ➛</b> {username}"
    )

    msg = await app.send_message(chat_id, text)
    asyncio.create_task(delete_message_after_delay(chat_id, msg.id))


@fl.call_participant(GroupCallParticipant.Action.JOINED)
async def participant_join(_, update: UpdatedGroupCallParticipant):
    chat_id = update.chat_id
    user_id = update.participant.user_id

    if chat_id not in enabled_chats:
        return

    await send_join_notification(chat_id, user_id)


@fl.call_participant(GroupCallParticipant.Action.LEFT)
async def participant_left(_, update: UpdatedGroupCallParticipant):
    chat_id = update.chat_id
    user_id = update.participant.user_id

    if chat_id not in enabled_chats:
        return

    await send_leave_notification(chat_id, user_id)


@app.on_message(filters.command(["vclogger", "vclog"]) & filters.group)
async def vclogger_cmd(_, message: Message):
    chat_id = message.chat.id

    member = await app.get_chat_member(chat_id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        return await message.reply_text("❌ Admin only!")

    if len(message.command) < 2:
        status = "ON" if chat_id in enabled_chats else "OFF"
        return await message.reply_text(
            f"📊 VC Logger: {status}\n\n"
            "Commands:\n"
            "/vclogger on\n"
            "/vclogger off"
        )

    action = message.command[1].lower()

    if action == "on":
        enabled_chats.add(chat_id)
        await message.reply_text("✅ VC Logger Enabled!")
    elif action == "off":
        enabled_chats.discard(chat_id)
        await message.reply_text("❌ VC Logger Disabled!")
    else:
        await message.reply_text("Use: /vclogger on | off")


# Register handlers after PyTgCalls clients are started
async def register_vc_logger():
    try:
        await asyncio.sleep(10)
        for client in anon.clients:
            client.add_handler(participant_join)
            client.add_handler(participant_left)
        logger.info("VC Logger handlers registered.")
    except Exception as e:
        logger.error(f"Failed to register VC logger handlers: {e}")


asyncio.create_task(register_vc_logger())
