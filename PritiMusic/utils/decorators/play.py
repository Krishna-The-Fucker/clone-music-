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
    Config me image URL string ya list ho sakti hai.
    Pyrogram ko single URL return karta hai.
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
        if message.command:
            return str(message.command[0]).lower()
    except Exception:
        pass

    return ""


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
    Play request ka logger.

    Main bot:
        play_logs()

    Clone bot:
        clone_bot_logs()

    Logger me error aane par playback nahi rukega.
    """

    try:

        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------

        if url:
            streamtype = "YouTube"

        elif audio_telegram:
            streamtype = "Telegram Audio"

        elif video_telegram:
            streamtype = "Telegram Video"

        else:
            streamtype = "Search"

        # -------------------------------------------------
        # CHECK CLONE / MAIN
        # -------------------------------------------------

        try:
            main_me = await app.get_me()
            client_me = await client.get_me()

            is_clone = (
                client_me.id != main_me.id
            )

        except Exception:
            is_clone = False

        # -------------------------------------------------
        # CLONE LOGGER
        # -------------------------------------------------

        if is_clone:

            try:

                await clone_bot_logs(
                    client=client,
                    message=message,
                    streamtype=streamtype,
                )

            except Exception as e:

                print(
                    "[PLAY LOGGER ERROR] "
                    f"Clone logger: "
                    f"{type(e).__name__}: {e}"
                )

        # -------------------------------------------------
        # MAIN LOGGER
        # -------------------------------------------------

        else:

            try:

                await play_logs(
                    message,
                    streamtype,
                )

            except Exception as e:

                print(
                    "[PLAY LOGGER ERROR] "
                    f"Main logger: "
                    f"{type(e).__name__}: {e}"
                )

    except Exception as e:

        print(
            "[PLAY LOGGER ERROR] "
            f"{type(e).__name__}: {e}"
        )


# =========================================================
# PLAY WRAPPER
# =========================================================

def PlayWrapper(command):

    async def wrapper(client, message):

        # =================================================
        # LANGUAGE
        # =================================================

        try:

            language = await get_lang(
                message.chat.id
            )

            _ = get_string(language)

        except Exception as e:

            print(
                "[LANGUAGE ERROR] "
                f"{type(e).__name__}: {e}"
            )

            # Fallback language
            try:
                _ = get_string("en")
            except Exception:
                return await message.reply_text(
                    "Language configuration error."
                )

        # =================================================
        # SENDER CHAT CHECK
        # =================================================

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

        # =================================================
        # MAINTENANCE
        # =================================================

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
                        f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, "
                        f"ᴠɪsɪᴛ <a href='{SUPPORT_CHAT}'>"
                        f"sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ "
                        f"ᴛʜᴇ ʀᴇᴀsᴏɴ."
                    ),
                    disable_web_page_preview=True,
                )

        # =================================================
        # COMMAND NAME
        # =================================================

        command_name = get_command_name(
            message
        )

        # =================================================
        # TELEGRAM MEDIA
        # =================================================

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

        except Exception as e:

            print(
                "[MEDIA CHECK ERROR] "
                f"{type(e).__name__}: {e}"
            )

        # =================================================
        # YOUTUBE URL
        # =================================================

        try:

            url = await YouTube.url(
                message
            )

        except Exception as e:

            print(
                "[YOUTUBE URL ERROR] "
                f"{type(e).__name__}: {e}"
            )

            url = None

        # =================================================
        # NO INPUT
        # =================================================

        if (
            audio_telegram is None
            and video_telegram is None
            and url is None
        ):

            try:

                command_length = len(
                    message.command
                    or []
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

        # =================================================
        # CHAT MODE
        # =================================================

        if command_name.startswith("c"):

            chat_id = await get_cmode(
                message.chat.id
            )

            if chat_id is None:

                return await message.reply_text(
                    _["setting_7"]
                )

            try:

                chat = await app.get_chat(
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

        # =================================================
        # PLAY SETTINGS
        # =================================================

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

        # =================================================
        # ADMIN CHECK
        # =================================================

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

        # =================================================
        # VIDEO FLAG
        # =================================================

        try:

            command_text = (
                message.text
                or message.caption
                or ""
            )

        except Exception:

            command_text = ""

        video = None

        # /vplay
        if command_name.startswith("v"):

            video = True

        # /play -v
        elif "-v" in command_text.lower():

            video = True

        # /play v
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

        # =================================================
        # FORCE PLAY
        # =================================================

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

        # =================================================
        # ASSISTANT CHECK
        # =================================================

        try:

            active_chat = await is_active_chat(
                chat_id
            )

        except Exception:

            active_chat = False

        if not active_chat:

            userbot = await get_assistant(
                chat_id
            )

            if not userbot:

                return await message.reply_text(
                    _["call_1"]
                )

            # =================================================
            # ASSISTANT MEMBER CHECK
            # =================================================

            try:

                try:

                    member = (
                        await app.get_chat_member(
                            chat_id,
                            userbot.id,
                        )
                    )

                except ChatAdminRequired:

                    return await message.reply_text(
                        _["call_1"]
                    )

                # =================================================
                # BANNED / RESTRICTED
                # =================================================

                if member.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):

                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention,
                            userbot.id,
                            userbot.name,
                            userbot.username,
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text=(
                                            "๏ 𝗨ɴʙᴀɴ "
                                            "𝗔ssɪsᴛᴀɴᴛ ๏"
                                        ),
                                        callback_data=(
                                            "unban_assistant"
                                        ),
                                    )
                                ]
                            ]
                        ),
                    )

            # =================================================
            # ASSISTANT NOT IN GROUP
            # =================================================

            except UserNotParticipant:

                # =============================================
                # GET INVITE LINK
                # =============================================

                invitelink = links.get(
                    chat_id
                )

                if not invitelink:

                    # -----------------------------------------
                    # PUBLIC GROUP
                    # -----------------------------------------

                    if getattr(
                        message.chat,
                        "username",
                        None,
                    ):

                        invitelink = (
                            message.chat.username
                        )

                        try:

                            await userbot.resolve_peer(
                                invitelink
                            )

                        except Exception:

                            pass

                    # -----------------------------------------
                    # PRIVATE GROUP
                    # -----------------------------------------

                    else:

                        try:

                            invitelink = (
                                await app.export_chat_invite_link(
                                    chat_id
                                )
                            )

                        except ChatAdminRequired:

                            return await message.reply_text(
                                _["call_1"]
                            )

                        except Exception as e:

                            return await message.reply_text(
                                _["call_3"].format(
                                    app.mention,
                                    type(e).__name__,
                                )
                            )

                # =============================================
                # NORMALIZE INVITE LINK
                # =============================================

                if (
                    invitelink
                    and invitelink.startswith(
                        "https://t.me/+"
                    )
                ):

                    invitelink = (
                        invitelink.replace(
                            "https://t.me/+",
                            "https://t.me/joinchat/",
                        )
                    )

                # =============================================
                # JOIN MESSAGE
                # =============================================

                myu = await message.reply_text(
                    _["call_4"].format(
                        app.mention
                    )
                )

                try:

                    await asyncio.sleep(1)

                    await userbot.join_chat(
                        invitelink
                    )

                # =============================================
                # JOIN REQUEST
                # =============================================

                except InviteRequestSent:

                    try:

                        await app.approve_chat_join_request(
                            chat_id,
                            userbot.id,
                        )

                    except Exception as e:

                        return await message.reply_text(
                            _["call_3"].format(
                                app.mention,
                                type(e).__name__,
                            )
                        )

                    await asyncio.sleep(3)

                    try:

                        await myu.edit(
                            _["call_5"].format(
                                app.mention
                            )
                        )

                    except Exception:

                        pass

                # =============================================
                # ALREADY PARTICIPANT
                # =============================================

                except UserAlreadyParticipant:

                    pass

                # =============================================
                # OTHER ERROR
                # =============================================

                except Exception as e:

                    return await message.reply_text(
                        _["call_3"].format(
                            app.mention,
                            type(e).__name__,
                        )
                    )

                # =============================================
                # SAVE INVITE LINK
                # =============================================

                if invitelink:

                    links[
                        chat_id
                    ] = invitelink

                # =============================================
                # RESOLVE CHAT
                # =============================================

                try:

                    await userbot.resolve_peer(
                        chat_id
                    )

                except Exception:

                    pass

        # =================================================
        # PLAY LOGGER
        #
        # IMPORTANT:
        # Permission / assistant checks ke BAAD logger.
        # Isse invalid / rejected play request log nahi hogi.
        # =================================================

        await send_play_logger(
            client=client,
            message=message,
            url=url,
            audio_telegram=audio_telegram,
            video_telegram=video_telegram,
        )

        # =================================================
        # DELETE COMMAND
        #
        # Logger ke baad delete kar rahe hain taaki logger
        # ko original message ka query mil sake.
        # =================================================

        try:

            await message.delete()

        except Exception:

            pass

        # =================================================
        # ACTUAL PLAY FUNCTION
        # =================================================

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


# =========================================================
# CPLAY WRAPPER
# =========================================================
#
# Project ke purane files:
#
# from PritiMusic.utils.decorators.play import CPlayWrapper
#
# use kar sakte hain.
#
# Isko alias rakhna intentionally hai.
# =========================================================

def CPlayWrapper(command):
    return PlayWrapper(command)


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

__all__ = [
    "PlayWrapper",
    "CPlayWrapper",
    ]
