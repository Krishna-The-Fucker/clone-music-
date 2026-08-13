from pyrogram.enums import ParseMode

from PritiMusic import app
from config import LOGGER_ID, CLONE_LOGGER_ID


# =========================================================
# SAFE HELPERS
# =========================================================

def safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def get_user_text(user):
    if not user:
        return "Unknown"

    try:
        name = user.mention
    except Exception:
        name = getattr(user, "first_name", None) or "Unknown"

    username = (
        f"@{user.username}"
        if getattr(user, "username", None)
        else "No Username"
    )

    user_id = getattr(user, "id", "Unknown")

    return (
        f"{name}\n"
        f"<b>Username:</b> {username}\n"
        f"<b>ID:</b> <code>{user_id}</code>"
    )


def get_chat_text(chat):
    if not chat:
        return "Unknown"

    title = (
        getattr(chat, "title", None)
        or getattr(chat, "first_name", None)
        or "Unknown"
    )

    chat_id = getattr(chat, "id", "Unknown")

    username = getattr(chat, "username", None)

    if username:
        link = f"https://t.me/{username}"
    else:
        link = "Private Group"

    return (
        f"<b>{title}</b>\n"
        f"<b>ID:</b> <code>{chat_id}</code>\n"
        f"<b>Link:</b> {link}"
    )


async def get_query(message):
    try:
        text = getattr(message, "text", None)

        if text:
            parts = text.split(None, 1)

            if len(parts) > 1:
                return parts[1][:1000]

        caption = getattr(message, "caption", None)

        if caption:
            parts = caption.split(None, 1)

            if len(parts) > 1:
                return parts[1][:1000]

    except Exception:
        pass

    return "Link / File / Reply"


def get_source(message, streamtype=None):
    if streamtype:
        return str(streamtype)

    try:
        if message.reply_to_message:

            if message.reply_to_message.audio:
                return "Telegram Audio"

            if message.reply_to_message.voice:
                return "Telegram Voice"

            if message.reply_to_message.video:
                return "Telegram Video"

            if message.reply_to_message.document:
                return "Telegram Document"

        text = (
            getattr(message, "text", None)
            or getattr(message, "caption", None)
            or ""
        )

        text_lower = text.lower()

        if "youtube.com" in text_lower:
            return "YouTube"

        if "youtu.be" in text_lower:
            return "YouTube"

        if "spotify.com" in text_lower:
            return "Spotify"

    except Exception:
        pass

    return "Unknown"


# =========================================================
# MAIN BOT PLAY LOGGER
# =========================================================

async def play_logs(message, streamtype="Unknown"):
    """
    Main bot ke play logs LOGGER_ID me bhejta hai.
    """

    try:

        logger_id = safe_int(LOGGER_ID)

        if not logger_id:
            print("[LOGGER] LOGGER_ID is not configured.")
            return False

        if not message:
            return False

        if message.chat and message.chat.id == logger_id:
            return False

        bot = await app.get_me()

        query = await get_query(message)

        user_text = get_user_text(
            getattr(message, "from_user", None)
        )

        chat_text = get_chat_text(
            getattr(message, "chat", None)
        )

        source = get_source(
            message,
            streamtype
        )

        logger_text = f"""
<b>🎵 {bot.mention} ᴘʟᴀʏ ʟᴏɢ</b>

━━━━━━━━━━━━━━━━━━━━

<b>👤 ᴘʟᴀʏᴇᴅ ʙʏ:</b>
{user_text}

<b>🎶 ǫᴜᴇʀʏ:</b>
<code>{query}</code>

<b>📡 sᴏᴜʀᴄᴇ:</b>
<code>{source}</code>

<b>👥 ᴄʜᴀᴛ:</b>
{chat_text}

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}
<b>ID:</b> <code>{bot.id}</code>

━━━━━━━━━━━━━━━━━━━━
"""

        await app.send_message(
            chat_id=logger_id,
            text=logger_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        print(
            f"[LOGGER] Main play log sent | "
            f"chat={message.chat.id}"
        )

        return True

    except Exception as e:

        print(
            f"[LOGGER ERROR] play_logs: "
            f"{type(e).__name__}: {e}"
        )

        return False


# =========================================================
# CLONE BOT PLAY LOGGER
# =========================================================

async def clone_bot_logs(
    client,
    message,
    bot_mention=None,
    clone_logger_id=None,
    streamtype="Unknown",
):
    """
    Clone bot ka play log:

    1. Clone logger
    2. Main logger
    """

    try:

        bot = await client.get_me()

        if not bot_mention:
            bot_mention = bot.mention

        query = await get_query(message)

        user_text = get_user_text(
            getattr(message, "from_user", None)
        )

        chat_text = get_chat_text(
            getattr(message, "chat", None)
        )

        source = get_source(
            message,
            streamtype
        )

        # =================================================
        # CLONE LOGGER
        # =================================================

        target_clone_logger = (
            clone_logger_id
            or CLONE_LOGGER_ID
        )

        target_clone_logger = safe_int(
            target_clone_logger
        )

        if target_clone_logger:

            clone_text = f"""
<b>🎵 ᴄʟᴏɴᴇ ʙᴏᴛ ᴘʟᴀʏ ʟᴏɢ</b>

━━━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot_mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴘʟᴀʏᴇᴅ ʙʏ:</b>
{user_text}

<b>🎶 ǫᴜᴇʀʏ:</b>
<code>{query}</code>

<b>📡 sᴏᴜʀᴄᴇ:</b>
<code>{source}</code>

<b>👥 ᴄʜᴀᴛ:</b>
{chat_text}

━━━━━━━━━━━━━━━━━━━━
"""

            try:

                await client.send_message(
                    chat_id=target_clone_logger,
                    text=clone_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Clone play log sent."
                )

            except Exception as e:

                print(
                    "[LOGGER ERROR] Clone logger: "
                    f"{type(e).__name__}: {e}"
                )

        # =================================================
        # MAIN LOGGER
        # =================================================

        main_logger = safe_int(LOGGER_ID)

        if main_logger:

            main_text = f"""
<b>🤖 ᴄʟᴏɴᴇ ʙᴏᴛ ᴘʟᴀʏ</b>

━━━━━━━━━━━━━━━━━━━━

<b>🤖 ᴄʟᴏɴᴇ:</b>
{bot_mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴘʟᴀʏᴇᴅ ʙʏ:</b>
{user_text}

<b>🎶 ǫᴜᴇʀʏ:</b>
<code>{query}</code>

<b>📡 sᴏᴜʀᴄᴇ:</b>
<code>{source}</code>

<b>👥 ᴄʜᴀᴛ:</b>
{chat_text}

━━━━━━━━━━━━━━━━━━━━
"""

            try:

                await app.send_message(
                    chat_id=main_logger,
                    text=main_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Main clone play log sent."
                )

            except Exception as e:

                print(
                    "[LOGGER ERROR] Main logger: "
                    f"{type(e).__name__}: {e}"
                )

        return True

    except Exception as e:

        print(
            "[LOGGER ERROR] clone_bot_logs: "
            f"{type(e).__name__}: {e}"
        )

        return False


# =========================================================
# MAIN BOT START LOGGER
# =========================================================

async def bot_start_logs(client=None):
    """
    Main bot start hone par LOGGER_ID me message.
    """

    try:

        bot_client = client or app

        logger_id = safe_int(LOGGER_ID)

        if not logger_id:
            print(
                "[LOGGER] LOGGER_ID is not configured."
            )
            return False

        bot = await bot_client.get_me()

        text = f"""
<b>🚀 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

━━━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b>
@{bot.username or "None"}

<b>📌 sᴛᴀᴛᴜs:</b>
<code>ONLINE</code>

━━━━━━━━━━━━━━━━━━━━
"""

        await bot_client.send_message(
            chat_id=logger_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        print(
            f"[LOGGER] Bot start log sent: "
            f"@{bot.username}"
        )

        return True

    except Exception as e:

        print(
            "[LOGGER ERROR] bot_start_logs: "
            f"{type(e).__name__}: {e}"
        )

        return False


# =========================================================
# CLONE BOT START LOGGER
# =========================================================

async def clone_start_logs(client):
    """
    Clone bot start hone par:

    - CLONE_LOGGER_ID
    - LOGGER_ID

    dono jagah message bhejta hai.
    """

    try:

        bot = await client.get_me()

        text = f"""
<b>🟢 ᴄʟᴏɴᴇ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

━━━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b>
@{bot.username or "None"}

<b>📌 sᴛᴀᴛᴜs:</b>
<code>ONLINE</code>

━━━━━━━━━━━━━━━━━━━━
"""

        clone_logger = safe_int(
            CLONE_LOGGER_ID
        )

        main_logger = safe_int(
            LOGGER_ID
        )

        # =================================================
        # CLONE LOGGER
        # =================================================

        if clone_logger:

            try:

                await client.send_message(
                    chat_id=clone_logger,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Clone start log sent."
                )

            except Exception as e:

                print(
                    "[LOGGER ERROR] "
                    f"Clone start: {type(e).__name__}: {e}"
                )

        # =================================================
        # MAIN LOGGER
        # =================================================

        if main_logger:

            try:

                await app.send_message(
                    chat_id=main_logger,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Main clone-start log sent."
                )

            except Exception as e:

                print(
                    "[LOGGER ERROR] "
                    f"Main clone start: {type(e).__name__}: {e}"
                )

        return True

    except Exception as e:

        print(
            "[LOGGER ERROR] clone_start_logs: "
            f"{type(e).__name__}: {e}"
        )

        return False
