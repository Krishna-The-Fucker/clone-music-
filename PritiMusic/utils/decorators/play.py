# FIX for PritiMusic/utils/decorators/play.py
# Replace your existing file with the full code from this conversation,
# or at minimum apply the safe_photo() helper below.

import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
    PeerIdInvalid,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from PritiMusic import YouTube, app
from PritiMusic.misc import SUDOERS
from PritiMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from PritiMusic.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string

links = {}
clinks = {}


def safe_photo(value):
    # config.py uses .split(), therefore PLAYLIST_IMG_URL can be a list.
    # Pyrogram reply_photo() accepts one string/file object, NOT a list.
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None

    if not value:
        value = "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"

    return str(value)


def safe_support_chat(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    return str(value or "")


def get_user_info(userbot):
    if hasattr(userbot, "me") and userbot.me:
        me = userbot.me
        return me.id, me.username, me.first_name

    return (
        getattr(userbot, "id", 0),
        getattr(userbot, "username", None),
        getattr(userbot, "name", "Assistant"),
    )


def get_command_arg(message, index):
    try:
        return message.command[index]
    except (IndexError, TypeError, AttributeError):
        return ""


def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        if message.sender_chat:
            return await message.reply_text(
                _["general_3"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        text="ʜᴏᴡ ᴛᴏ ғɪx ?",
                        callback_data="LuckymousAdmin",
                    )]]
                ),
            )

        if await is_maintenance() is False:
            if message.from_user and message.from_user.id not in SUDOERS:
                support = safe_support_chat(SUPPORT_CHAT)
                return await message.reply_text(
                    f'{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ '
                    f'<a href="{support}">sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ '
                    f'ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.',
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except Exception:
            pass

        reply = message.reply_to_message

        audio_telegram = (
            (reply.audio or reply.voice) if reply else None
        )
        video_telegram = (
            (reply.video or reply.document) if reply else None
        )

        url = await YouTube.url(message)

        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])

                buttons = botplaylist_markup(_)

                # THE IMPORTANT FIX:
                # PLAYLIST_IMG_URL is a list because config.py calls .split().
                return await message.reply_photo(
                    photo=safe_photo(PLAYLIST_IMG_URL),
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])

            try:
                chat = await app.get_chat(chat_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])

            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        if playty != "Everyone" and (
            not message.from_user or message.from_user.id not in SUDOERS
        ):
            admins = adminlist.get(message.chat.id)
            if not admins:
                return await message.reply_text(_["admin_13"])
            if message.from_user.id not in admins:
                return await message.reply_text(_["play_4"])

        command_name = get_command_arg(message, 0)
        second_arg = get_command_arg(message, 1)

        if command_name.startswith("v"):
            video = True
        elif "-v" in (message.text or ""):
            video = True
        else:
            video = True if second_arg == "v" else None

        if command_name.endswith("e"):
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_16"])
            fplay = True
        else:
            fplay = None

        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            if not userbot:
                return await message.reply_text(_["call_1"])

            ub_id, ub_username, ub_name = get_user_info(userbot)

            try:
                try:
                    get = await app.get_chat_member(chat_id, ub_id)
                except (ChatAdminRequired, PeerIdInvalid):
                    return await message.reply_text(_["call_1"])

                if get.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):
                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention, ub_id, ub_name, ub_username
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(
                                text="๏ 𝗨ɴʙᴀɴ 𝗔ssɪsᴛᴀɴᴛ ๏",
                                callback_data="unban_assistant",
                            )]]
                        ),
                    )

            except UserNotParticipant:
                if chat_id in links:
                    invitelink = links[chat_id]
                elif message.chat.username:
                    invitelink = message.chat.username
                    try:
                        await userbot.resolve_peer(invitelink)
                    except Exception:
                        pass
                else:
                    try:
                        invitelink = await app.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        return await message.reply_text(_["call_1"])
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )

                myu = await message.reply_text(_["call_4"].format(app.mention))

                try:
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)
                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_id, ub_id)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                    await asyncio.sleep(3)
                    await myu.edit(_["call_5"].format(app.mention))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        _["call_3"].format(app.mention, type(e).__name__)
                    )

                links[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(chat_id)
                except Exception:
                    pass

        return await command(
            client, message, _, chat_id, video,
            channel, playmode, url, fplay
        )

    return wrapper


def CPlayWrapper(command):
    async def wrapper(client, message):
        i = await client.get_me()
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        if message.sender_chat:
            return await message.reply_text(
                _["general_3"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        text="ʜᴏᴡ ᴛᴏ ғɪx ?",
                        callback_data="LuckymousAdmin",
                    )]]
                ),
            )

        if await is_maintenance() is False:
            if message.from_user and message.from_user.id not in SUDOERS:
                support = safe_support_chat(SUPPORT_CHAT)
                return await message.reply_text(
                    f'{i.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ '
                    f'<a href="{support}">sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ '
                    f'ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.',
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except Exception:
            pass

        reply = message.reply_to_message

        audio_telegram = (
            (reply.audio or reply.voice) if reply else None
        )
        video_telegram = (
            (reply.video or reply.document) if reply else None
        )

        url = await YouTube.url(message)

        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])

                buttons = botplaylist_markup(_)

                # SAME FIX HERE
                return await message.reply_photo(
                    photo=safe_photo(PLAYLIST_IMG_URL),
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])

            try:
                chat = await client.get_chat(chat_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])

            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        if playty != "Everyone" and (
            not message.from_user or message.from_user.id not in SUDOERS
        ):
            admins = adminlist.get(message.chat.id)
            if not admins:
                return await message.reply_text(_["admin_13"])
            if message.from_user.id not in admins:
                return await message.reply_text(_["play_4"])

        command_name = get_command_arg(message, 0)
        second_arg = get_command_arg(message, 1)

        if command_name.startswith("v"):
            video = True
        elif "-v" in (message.text or ""):
            video = True
        else:
            video = True if second_arg == "v" else None

        if command_name.endswith("e"):
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_16"])
            fplay = True
        else:
            fplay = None

        if not await is_active_chat(chat_id):
            if hasattr(client, "assistant") and client.assistant:
                userbot = client.assistant
            else:
                userbot = await get_assistant(chat_id)

            if not userbot:
                return await message.reply_text(_["call_1"])

            ub_id, ub_username, ub_name = get_user_info(userbot)

            try:
                try:
                    get = await userbot.get_chat_member(chat_id, "me")
                except Exception:
                    raise UserNotParticipant

                if get.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):
                    return await message.reply_text(
                        _["call_2"].format(
                            i.mention, ub_id, ub_name, ub_username
                        )
                    )

            except UserNotParticipant:
                if chat_id in clinks:
                    invitelink = clinks[chat_id]
                elif message.chat.username:
                    invitelink = message.chat.username
                    try:
                        await userbot.resolve_peer(invitelink)
                    except Exception:
                        pass
                else:
                    try:
                        invitelink = await client.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        return await message.reply_text(_["call_1"])
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(i.mention, type(e).__name__)
                        )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+",
                        "https://t.me/joinchat/",
                    )

                myu = await message.reply_text(_["call_4"].format(i.mention))

                try:
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)
                except InviteRequestSent:
                    try:
                        await client.approve_chat_join_request(chat_id, ub_id)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(i.mention, type(e).__name__)
                        )
                    await asyncio.sleep(3)
                    await myu.edit(_["call_5"].format(i.mention))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        _["call_3"].format(i.mention, type(e).__name__)
                    )

                clinks[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(chat_id)
                except Exception:
                    pass

        return await command(
            client, message, _, chat_id, video,
            channel, playmode, url, fplay
        )

    return wrapper
