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
    get_assistant() se Client milta hai.

    Client ke andar directly:
        userbot.id
        userbot.name
        userbot.username

    use nahi karna.

    get_me() se actual Telegram User object milta hai.
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
# ASSISTANT MEMBER CHECK
# =========================================================

async def get_assistant_member(chat_id, assistant_id):
    """
    Assistant ka current membership status safely check karta hai.
    """

    try:

        return await app.get_chat_member(
            chat_id,
            assistant_id,
        )

    except UserNotParticipant:

        return None

    except ChatAdminRequired:

        print(
            "[ASSISTANT CHECK] "
            "Bot ko chat members check karne ki permission nahi hai."
        )

        return None

    except Exception as e:

        print(
            "[ASSISTANT MEMBER ERROR] "
            f"{type(e).__name__}: {e}"
        )

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
    Logger fail hone par playback ko kabhi stop nahi karega.
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
        # MAIN / CLONE CHECK
        # -------------------------------------------------

        try:

            main_me = await app.get_me()
            client_me = await client.get_me()

            is_clone = (
                client_me.id != main_me.id
            )

        except Exception as e:

            print(
                "[PLAY LOGGER BOT CHECK ERROR] "
                f"{type(e).__name__}: {e}"
            )

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
                    f"Clone: {type(e).__name__}: {e}"
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
                    f"Main: {type(e).__name__}: {e}"
                )

    except Exception as e:

        print(
            "[PLAY LOGGER ERROR] "
            f"{type(e).__name__}: {e}"
        )


# =========================================================
# ASSISTANT JOIN
# =========================================================

async def ensure_assistant_joined(
    message,
    chat_id,
    userbot,
    assistant,
    _,
):
    """
    Assistant ko group me ensure karta hai.

    Return:
        True  = assistant ready
        False = assistant ready nahi hua
    """

    assistant_id = assistant.id

    assistant_name = (
        assistant.first_name
        or "Assistant"
    )

    assistant_username = (
        f"@{assistant.username}"
        if assistant.username
        else "No Username"
    )

    # =====================================================
    # CURRENT MEMBER CHECK
    # =====================================================

    try:

        member = await app.get_chat_member(
            chat_id,
            assistant_id,
        )

        # -------------------------------------------------
        # BANNED
        # -------------------------------------------------

        if member.status == ChatMemberStatus.BANNED:

            await message.reply_text(
                _["call_2"].format(
                    app.mention,
                    assistant_id,
                    assistant_name,
                    assistant_username,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=(
                                    "๏ 𝗨ɴʙᴀɴ "
                                    "𝗔ssɪsᴛᴀɴᴛ ๏"
                                ),
                                callback_data="unban_assistant",
                            )
                        ]
                    ]
                ),
            )

            return False

        # -------------------------------------------------
        # RESTRICTED
        # -------------------------------------------------

        if member.status == ChatMemberStatus.RESTRICTED:

            await message.reply_text(
                _["call_2"].format(
                    app.mention,
                    assistant_id,
                    assistant_name,
                    assistant_username,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=(
                                    "๏ 𝗨ɴʙᴀɴ "
                                    "𝗔ssɪsᴛᴀɴᴛ ๏"
                                ),
                                callback_data="unban_assistant",
                            )
                        ]
                    ]
                ),
            )

            return False

        # -------------------------------------------------
        # ALREADY IN GROUP
        # -------------------------------------------------

        if member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ):

            try:
                await userbot.resolve_peer(chat_id)
            except Exception:
                pass

            return True

    except UserNotParticipant:

        pass

    except ChatAdminRequired:

        await message.reply_text(
            _["call_1"]
        )

        return False

    except Exception as e:

        print(
            "[ASSISTANT MEMBER CHECK ERROR] "
            f"{type(e).__name__}: {e}"
        )

    # =====================================================
    # ASSISTANT NOT IN GROUP
    # =====================================================

    invitelink = links.get(chat_id)

    # =====================================================
    # PUBLIC GROUP
    # =====================================================

    if not invitelink:

        try:

            username = getattr(
                message.chat,
                "username",
                None,
            )

            if username:

                invitelink = username

        except Exception:
            invitelink = None

    # =====================================================
    # PRIVATE GROUP
    # =====================================================

    if not invitelink:

        try:

            # -------------------------------------------------
            # IMPORTANT:
            # Bot ko "Invite Users via Link" permission
            # chahiye.
            # -------------------------------------------------

            invitelink = (
                await app.export_chat_invite_link(
                    chat_id
                )
            )

        except ChatAdminRequired:

            await message.reply_text(
                _["call_1"]
            )

            print(
                "[ASSISTANT JOIN] "
                "Bot needs Invite Users via Link permission."
            )

            return False

        except Exception as e:

            error_name = type(e).__name__

            print(
                "[ASSISTANT INVITE ERROR] "
                f"{error_name}: {e}"
            )

            # -------------------------------------------------
            # Clear permission message
            # -------------------------------------------------

            try:

                await message.reply_text(
                    (
                        "❌ <b>Assistant group me join nahi ho saka.</b>\n\n"
                        "Bot ko group me <b>Invite Users via Link</b> "
                        "permission do.\n\n"
                        "Phir <code>/play</code> dobara try karo."
                    )
                )

            except Exception:
                pass

            return False

    # =====================================================
    # NORMALIZE INVITE LINK
    # =====================================================

    if (
        invitelink
        and invitelink.startswith(
            "https://t.me/+"
        )
    ):

        invitelink = invitelink.replace(
            "https://t.me/+",
            "https://t.me/joinchat/",
        )

    # =====================================================
    # SAVE LINK
    # =====================================================

    if invitelink:

        links[chat_id] = invitelink

    # =====================================================
    # ASSISTANT JOIN MESSAGE
    # =====================================================

    try:

        join_message = await message.reply_text(
            _["call_4"].format(
                app.mention
            )
        )

    except Exception:

        join_message = None

    # =====================================================
    # JOIN
    # =====================================================

    try:

        await asyncio.sleep(1)

        await userbot.join_chat(
            invitelink
        )

    # =====================================================
    # JOIN REQUEST
    # =====================================================

    except InviteRequestSent:

        try:

            await app.approve_chat_join_request(
                chat_id,
                assistant_id,
            )

        except Exception as e:

            print(
                "[ASSISTANT APPROVE ERROR] "
                f"{type(e).__name__}: {e}"
            )

            try:

                await message.reply_text(
                    (
                        "❌ Assistant ka join request "
                        "approve nahi ho saka.\n\n"
                        f"<code>{type(e).__name__}</code>"
                    )
                )

            except Exception:
                pass

            return False

        await asyncio.sleep(3)

        if join_message:

            try:

                await join_message.edit(
                    _["call_5"].format(
                        app.mention
                    )
                )

            except Exception:
                pass

    # =====================================================
    # ALREADY PARTICIPANT
    # =====================================================

    except UserAlreadyParticipant:

        pass

    # =====================================================
    # OTHER JOIN ERROR
    # =====================================================

    except Exception as e:

        print(
            "[ASSISTANT JOIN ERROR] "
            f"{type(e).__name__}: {e}"
        )

        try:

            await message.reply_text(
                (
                    "❌ <b>Assistant join failed.</b>\n\n"
                    f"<code>{type(e).__name__}: {e}</code>"
                )
            )

        except Exception:
            pass

        return False

    # =====================================================
    # RESOLVE CHAT
    # =====================================================

    try:

        await userbot.resolve_peer(
            chat_id
        )

    except Exception as e:

        print(
            "[ASSISTANT RESOLVE ERROR] "
            f"{type(e).__name__}: {e}"
        )

    # =====================================================
    # VERIFY AGAIN
    # =====================================================

    await asyncio.sleep(2)

    try:

        member = await app.get_chat_member(
            chat_id,
            assistant_id,
        )

        if member.status in (
            ChatMemberStatus.BANNED,
            ChatMemberStatus.RESTRICTED,
        ):

            return False

    except UserNotParticipant:

        print(
            "[ASSISTANT VERIFY] "
            "Assistant is still not in group."
        )

        try:

            await message.reply_text(
                (
                    "❌ Assistant abhi group me join nahi hua.\n"
                    "Please bot ki invite permission check karo."
                )
            )

        except Exception:
            pass

        return False

    except Exception as e:

        print(
            "[ASSISTANT VERIFY ERROR] "
            f"{type(e).__name__}: {e}"
        )

    return True


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

            try:

                _ = get_string("en")

            except Exception:

                return await message.reply_text(
                    "Language configuration error."
                )

        # =================================================
        # SENDER CHAT
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
        # COMMAND
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
        # YOUTUBE
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
        # VIDEO
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
        # ASSISTANT ACTIVE CHECK
        # =================================================

        try:

            active_chat = await is_active_chat(
                chat_id
            )

        except Exception:

            active_chat = False

        # =================================================
        # ASSISTANT
        # =================================================

        if not active_chat:

            try:

                userbot = await get_assistant(
                    chat_id
                )

            except Exception as e:

                print(
                    "[GET ASSISTANT ERROR] "
                    f"{type(e).__name__}: {e}"
                )

                userbot = None

            if not userbot:

                return await message.reply_text(
                    _["call_1"]
                )

            # -------------------------------------------------
            # IMPORTANT FIX
            # -------------------------------------------------

            assistant = await get_assistant_info(
                userbot
            )

            if not assistant:

                return await message.reply_text(
                    _["call_1"]
                )

            # -------------------------------------------------
            # ASSISTANT JOIN
            # -------------------------------------------------

            ready = await ensure_assistant_joined(
                message=message,
                chat_id=chat_id,
                userbot=userbot,
                assistant=assistant,
                _=_,
            )

            if not ready:

                return

        # =================================================
        # PLAY LOGGER
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
        # =================================================

        try:

            await message.delete()

        except Exception:
            pass

        # =================================================
        # ACTUAL PLAY
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

def CPlayWrapper(command):
    return PlayWrapper(command)


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "PlayWrapper",
    "CPlayWrapper",
            ]
