# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic
#ALONE-CODER

import asyncio
from pyrogram import enums, filters, types

from AloneX import app, config, db, lang
from AloneX.helpers import buttons, utils

# Start messages
START_PM_TEXT = (
    "<b>──「 𝔼𝕀𝕂𝕆 𝔹𝕆𝕋 ℝ𝔼ℙ𝕆 」──</b>\n\n"
    "<blockquote><b>𝐄ɪᴋᴏ 𝐁ᴏᴛ 𝐑ᴇᴩᴏ 𝐍ᴏᴡ 𝐏ᴜʙʟɪᴄ.</b></blockquote>\n"
    "<blockquote><b>𝐕ᴩꜱ & 𝐇ᴇʀᴏᴋᴜ 𝐃ᴏɴᴏ 𝐒ᴜᴩᴩᴏʀᴛᴇᴅ.</b></blockquote>\n"
    "<blockquote><b><u>𝐍ᴏᴛᴇ : 𝐃ᴏɴᴏ 𝐑ᴇᴩᴏ 𝐇ᴏꜱᴛ 𝐊ᴀʀɴᴀ 𝐏ᴀᴅᴇɢᴀ 𝐀ɢᴀʀ 𝐃ᴏɴᴏ 𝐇ᴏꜱᴛ 𝐍ᴀʜɪ 𝐊ᴀʀᴀ 𝐓ᴏ 𝐌ᴜꜱɪᴄ 𝐒ʏꜱᴛᴀʏᴍ 𝐊ᴀᴀᴍ 𝐍ᴀʜɪ 𝐊ᴀʀᴇɢᴀ.</u></b></blockquote>"
)


@app.on_message(filters.command(["music"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    await m.reply_text(
        text=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
    )


@app.on_message(filters.command(["repo"]))
@lang.language()
async def start(_, message: types.Message):
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE
    _text = (
        START_PM_TEXT.format(message.from_user.first_name, app.name)
        if private
        else START_PM_TEXT.format(app.name)
    )

    key = buttons.start_key(message.lang, private)
    await message.reply_photo(
        photo=config.START_IMG,
        caption=_text,
        reply_markup=key,
        quote=not private,
    )

    if private:
        if await db.is_user(message.from_user.id):
            return
        # await utils.send_log(message)
        await db.add_user(message.from_user.id)
    else:
        if await db.is_chat(message.chat.id):
            return
        # await utils.send_log(message, True)
        await db.add_chat(message.chat.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, cmd_delete, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            # await utils.send_log(message, True)
            await db.add_chat(message.chat.id)
