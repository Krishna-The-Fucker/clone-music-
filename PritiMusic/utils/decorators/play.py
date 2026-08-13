import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

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

from PritiMusic.utils.logger import (
    play_logs,
    clone_bot_logs,
)

from config import (
    PLAYLIST_IMG_URL,
    SUPPORT_CHAT,
    adminlist,
)

from strings import get_string


# =========================================================
# ASSISTANT INVITE LINK CACHE
# =========================================================

links = {}
clinks = {}


# =========================================================
# IMAGE HELPER
# =========================================================

def get_image(value):
    """
    Config me image URL string ya list/tuple ho sakti hai.
    """

    if isinstance(value, (list, tuple)):
        return value[0] if value else None

    return value


# =========================================================
# COMMAND HELPER
# =========================================================

def get_command_name(message):
    """
    Safe command name.
    """

    try:
        command = getattr(message, "command", None)

        if command:
            return str(command[0]).lower()

    except Exception:
        pass

    return ""


# =========================================================
# ASSISTANT INFO
# =========================================================

async def get_assistant_info(userbot):
    """
    get_assistant() se Pyrogram Client milta hai.
    """

    try:

        if not userbot:
            return None

        assistant = await userbot.get_me()

        return assistant

    except Exception as e:

        print(
            "[ASSISTANT INFO ERROR] "
            f"{type(e).__name__}: {e}"
        )

        return None


# =========================================================
# BOT MENTION HELPER
# =========================================================

async def get_client_mention(client):
    """
    Current bot / clone ka mention safely return karta hai.
    """

    try:

        me = await client.get_me()

        return me.mention

    except Exception:

        try:
            return app.mention
        except Exception:
            return "Bot"


# =========================================================
# ASSISTANT MEMBER CHECK
# =========================================================

async def get_assistant_member(
    client,
    chat_id,
    assistant_id,
):
    try:

        return await client.get_chat_member(
            chat_id,
            assistant_id,
        )

    except UserNotParticipant:

        return None

    except ChatAdminRequired:

        return None

    except Exception as e:

        return None


# =========================================================
# PLAY LOGGER
# =========================================================

async def send_play_logger(
    client,
    message,
    url=None,
    audio_telegram=None,
    video_telegram=None,
):
    """
    Logger fail hone par playback ko stop nahi karega.
    """

    try:

        if url:
            streamtype = "YouTube"

        elif audio_telegram:
            streamtype = "Telegram Audio"

        elif video_telegram:
            streamtype = "Telegram Video"

        else:
            streamtype = "Search"

        try:

            main_me = await app.get_me()
            client_me = await client.get_me()

            is_clone = (
                client_me.id != main_me.id
            )

        except Exception:
            is_clone = False

        if is_clone:

            try:

                await clone_bot_logs(
                    client=client,
                    message=message,
                    streamtype=streamtype,
                )

            except Exception:
                pass

        else:

            try:

                await play_logs(
                    message,
                    streamtype,
                )

            except Exception:
                pass

    except Exception:
        pass


# =========================================================
# ASSISTANT JOIN (BYPASSED TO PREVENT INVITE ERRORS)
# =========================================================

async def ensure_assistant_joined(
    client,
    message,
    chat_id,
    userbot,
    assistant,
    _,
):
    """
    Bypassed function to allow direct song play without invite link restrictions.
    Make sure your assistant account is already added to the group.
    """
    return True


# =========================================================
# PLAY WRAPPER
# =========================================================

def PlayWrapper(command):

    async def wrapper(client, message):

        try:

            language = await get_lang(
                message.chat.id
            )

            _ = get_string(
                language
            )

        except Exception:
            _ = get_string("en")

        bot_mention = await get_client_mention(
            client
        )

        try:

            if message.sender_chat:

                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ʜᴏᴡ ᴛᴏ ғɪx ?",
                                callback_data="LuckymousAdmin",
                            )
                        ]
                    ]
                )

                return await message.reply_text(
                    _["general_3"],
                    reply_markup=keyboard,
                )

        except Exception:
            pass

        try:
            maintenance = await is_maintenance()
        except Exception:
            maintenance = True

        if maintenance is False:

            if (
                not message.from_user
                or message.from_user.id not in SUDOERS
            ):

                return await message.reply_text(
                    text=(
                        f"{bot_mention} "
                        "ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, "
                        f"ᴠɪsɪᴛ <a href='{SUPPORT_CHAT}'>"
                        "sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ "
                        "ᴛʜᴇ ʀᴇᴀsᴏɴ."
                    ),
                    disable_web_page_preview=True,
                )

        command_name = get_command_name(
            message
        )

        audio_telegram = None
        video_telegram = None

        try:

            reply = message.reply_to_message

            if reply:

                audio_telegram = (
                    reply.audio
                    or reply.voice
                )

                video_telegram = (
                    reply.video
                    or reply.document
                )

        except Exception:
            pass

        try:

            url = await YouTube.url(
                message
            )

        except Exception:
            url = None

        if (
            audio_telegram is None
            and video_telegram is None
            and url is None
        ):

            try:

                command_length = len(
                    message.command or []
                )

            except Exception:
                command_length = 0

            if command_length < 2:

                if "stream" in command_name:

                    return await message.reply_text(
                        _["str_1"]
                    )

                try:

                    buttons = botplaylist_markup(
                        _
                    )

                    markup = InlineKeyboardMarkup(
                        buttons
                    )

                except Exception:
                    markup = None

                playlist_image = get_image(
                    PLAYLIST_IMG_URL
                )

                if not playlist_image:

                    return await message.reply_text(
                        _["play_18"],
                        reply_markup=markup,
                    )

                try:

                    return await message.reply_photo(
                        photo=playlist_image,
                        caption=_["play_18"],
                        reply_markup=markup,
                    )

                except Exception:

                    return await message.reply_text(
                        _["play_18"],
                        reply_markup=markup,
                    )

        if command_name.startswith("c"):

            chat_id = await get_cmode(
                message.chat.id
            )

            if chat_id is None:

                return await message.reply_text(
                    _["setting_7"]
                )

            try:
                chat = await client.get_chat(
                    chat_id
                )
            except Exception:
                return await message.reply_text(
                    _["cplay_4"]
                )

            channel = chat.title

        else:

            chat_id = message.chat.id
            channel = None

        try:
            playmode = await get_playmode(
                message.chat.id
            )
        except Exception:
            playmode = None

        try:
            playty = await get_playtype(
                message.chat.id
            )
        except Exception:
            playty = "Everyone"

        if playty != "Everyone":

            if (
                not message.from_user
                or message.from_user.id not in SUDOERS
            ):

                admins = adminlist.get(
                    message.chat.id
                )

                if not admins:

                    return await message.reply_text(
                        _["admin_13"]
                    )

                if (
                    message.from_user.id
                    not in admins
                ):

                    return await message.reply_text(
                        _["play_4"]
                    )

        try:
            command_text = (
                message.text
                or message.caption
                or ""
            )
        except Exception:
            command_text = ""

        video = None

        if command_name.startswith("v"):
            video = True
        elif "-v" in command_text.lower():
            video = True
        else:
            try:
                if (
                    len(message.command or []) > 1
                    and str(
                        message.command[1]
                    ).lower() == "v"
                ):
                    video = True
            except Exception:
                pass

        if command_name.endswith("e"):

            try:
                active = await is_active_chat(
                    chat_id
                )
            except Exception:
                active = False

            if not active:

                return await message.reply_text(
                    _["play_16"]
                )

            fplay = True

        else:
            fplay = None

        try:
            active_chat = await is_active_chat(
                chat_id
            )
        except Exception:
            active_chat = False

        if not active_chat:

            try:
                userbot = await get_assistant(
                    chat_id
                )
            except Exception:
                userbot = None

            if not userbot:
                return await message.reply_text(
                    _["call_1"]
                )

            assistant = await get_assistant_info(
                userbot
            )

            if not assistant:
                return await message.reply_text(
                    _["call_1"]
                )

            ready = await ensure_assistant_joined(
                client=client,
                message=message,
                chat_id=chat_id,
                userbot=userbot,
                assistant=assistant,
                _=_,
            )

            if not ready:
                return

        await send_play_logger(
            client=client,
            message=message,
            url=url,
            audio_telegram=audio_telegram,
            video_telegram=video_telegram,
        )

        try:
            await message.delete()
        except Exception:
            pass

        try:
            return await command(
                client,
                message,
                _,
                chat_id,
                video,
                channel,
                playmode,
                url,
                fplay,
            )
        except Exception as e:
            print(
                "[PLAY COMMAND ERROR] "
                f"{type(e).__name__}: {e}"
            )
            raise

    return wrapper


def CPlayWrapper(command):
    return PlayWrapper(
        command
    )


__all__ = [
    "PlayWrapper",
    "CPlayWrapper",
]
