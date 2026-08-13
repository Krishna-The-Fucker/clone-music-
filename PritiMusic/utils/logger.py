import html
import time

from pyrogram.enums import ParseMode

from PritiMusic import app
from config import LOGGER_ID, CLONE_LOGGER_ID


# =========================================================
# DUPLICATE PROTECTION
# =========================================================

# Same play event agar accidentally 2 baar call ho,
# to 8 seconds ke andar second message nahi bhejega.
_PLAY_LOG_CACHE = {}

# Same bot start event ko duplicate hone se rokega.
_START_LOG_CACHE = {}

DUPLICATE_WINDOW = 8


# =========================================================
# SAFE HELPERS
# =========================================================

def safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def esc(value):
    """
    Telegram HTML ke liye safe text.
    """
    try:
        return html.escape(str(value))
    except Exception:
        return "Unknown"


def is_duplicate(cache, key):
    """
    Check karta hai ki same event recently send hua hai ya nahi.
    """

    now = time.monotonic()

    old_time = cache.get(key)

    if old_time is not None:

        if now - old_time < DUPLICATE_WINDOW:
            return True

    cache[key] = now

    # Cache ko unnecessarily bada hone se rokna
    if len(cache) > 500:

        expired = [
            k
            for k, v in cache.items()
            if now - v > DUPLICATE_WINDOW
        ]

        for k in expired:
            cache.pop(k, None)

    return False


def get_user_text(user):

    if not user:
        return "Unknown"

    try:
        name = user.mention
    except Exception:
        name = getattr(
            user,
            "first_name",
            None,
        ) or "Unknown"

    username = getattr(
        user,
        "username",
        None,
    )

    if username:
        username_text = f"@{esc(username)}"
    else:
        username_text = "No Username"

    user_id = getattr(
        user,
        "id",
        "Unknown",
    )

    return (
        f"{name}\n"
        f"<b>Username:</b> {username_text}\n"
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

    chat_id = getattr(
        chat,
        "id",
        "Unknown",
    )

    username = getattr(
        chat,
        "username",
        None,
    )

    if username:

        link = (
            f"https://t.me/{esc(username)}"
        )

    else:

        link = "Private Group"

    return (
        f"<b>{esc(title)}</b>\n"
        f"<b>ID:</b> <code>{chat_id}</code>\n"
        f"<b>Link:</b> {link}"
    )


async def get_query(message):

    try:

        text = getattr(
            message,
            "text",
            None,
        )

        if text:

            parts = text.split(
                None,
                1,
            )

            if len(parts) > 1:

                return esc(
                    parts[1][:1000]
                )

        caption = getattr(
            message,
            "caption",
            None,
        )

        if caption:

            parts = caption.split(
                None,
                1,
            )

            if len(parts) > 1:

                return esc(
                    parts[1][:1000]
                )

    except Exception:
        pass

    return "Link / File / Reply"


def get_source(
    message,
    streamtype=None,
):

    if streamtype:
        return esc(streamtype)

    try:

        reply = getattr(
            message,
            "reply_to_message",
            None,
        )

        if reply:

            if getattr(
                reply,
                "audio",
                None,
            ):
                return "Telegram Audio"

            if getattr(
                reply,
                "voice",
                None,
            ):
                return "Telegram Voice"

            if getattr(
                reply,
                "video",
                None,
            ):
                return "Telegram Video"

            if getattr(
                reply,
                "document",
                None,
            ):
                return "Telegram Document"

        text = (
            getattr(
                message,
                "text",
                None,
            )
            or getattr(
                message,
                "caption",
                None,
            )
            or ""
        )

        text_lower = text.lower()

        if (
            "youtube.com" in text_lower
            or "youtu.be" in text_lower
        ):
            return "YouTube"

        if "spotify.com" in text_lower:
            return "Spotify"

    except Exception:
        pass

    return "Unknown"


# =========================================================
# PLAY DUPLICATE KEY
# =========================================================

async def get_play_key(
    message,
    bot_id,
):

    try:

        chat = getattr(
            message,
            "chat",
            None,
        )

        user = getattr(
            message,
            "from_user",
            None,
        )

        query = await get_query(
            message
        )

        chat_id = getattr(
            chat,
            "id",
            0,
        )

        user_id = getattr(
            user,
            "id",
            0,
        )

        return (
            bot_id,
            chat_id,
            user_id,
            query,
        )

    except Exception:

        return (
            bot_id,
            0,
            0,
            "unknown",
        )


# =========================================================
# MAIN BOT PLAY LOGGER
# =========================================================

async def play_logs(
    message,
    streamtype="Unknown",
):

    """
    Main bot ka play log.

    IMPORTANT:
    Sirf LOGGER_ID me ek message bhejta hai.
    """

    try:

        logger_id = safe_int(
            LOGGER_ID
        )

        if not logger_id:

            print(
                "[LOGGER] LOGGER_ID is not configured."
            )

            return False

        if not message:
            return False

        chat = getattr(
            message,
            "chat",
            None,
        )

        if chat and chat.id == logger_id:

            return False

        bot = await app.get_me()

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        play_key = await get_play_key(
            message,
            bot.id,
        )

        if is_duplicate(
            _PLAY_LOG_CACHE,
            play_key,
        ):

            print(
                "[LOGGER] Duplicate play log skipped."
            )

            return False

        # =================================================
        # DATA
        # =================================================

        query = await get_query(
            message
        )

        user_text = get_user_text(
            getattr(
                message,
                "from_user",
                None,
            )
        )

        chat_text = get_chat_text(
            chat
        )

        source = get_source(
            message,
            streamtype,
        )

        # =================================================
        # MESSAGE
        # =================================================

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

        # =================================================
        # SEND
        # =================================================

        await app.send_message(
            chat_id=logger_id,
            text=logger_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        print(
            "[LOGGER] Main play log sent."
        )

        return True

    except Exception as e:

        print(
            "[LOGGER ERROR] play_logs: "
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
    Clone bot ka play log.

    IMPORTANT:
    Agar LOGGER_ID aur CLONE_LOGGER_ID same hain,
    to sirf EK message jayega.

    Agar IDs alag hain:
        1. Clone logger
        2. Main logger

    dono me message ja sakta hai.
    """

    try:

        bot = await client.get_me()

        if not bot_mention:

            bot_mention = bot.mention

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        play_key = await get_play_key(
            message,
            bot.id,
        )

        clone_key = (
            "clone",
            play_key,
        )

        if is_duplicate(
            _PLAY_LOG_CACHE,
            clone_key,
        ):

            print(
                "[LOGGER] Duplicate clone play log skipped."
            )

            return False

        # =================================================
        # DATA
        # =================================================

        query = await get_query(
            message
        )

        user_text = get_user_text(
            getattr(
                message,
                "from_user",
                None,
            )
        )

        chat_text = get_chat_text(
            getattr(
                message,
                "chat",
                None,
            )
        )

        source = get_source(
            message,
            streamtype,
        )

        # =================================================
        # LOGGER IDS
        # =================================================

        target_clone_logger = safe_int(
            clone_logger_id
            or CLONE_LOGGER_ID
        )

        main_logger = safe_int(
            LOGGER_ID
        )

        # =================================================
        # CASE 1
        # SAME LOGGER ID
        # =================================================

        if (
            target_clone_logger
            and main_logger
            and target_clone_logger == main_logger
        ):

            text = f"""
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
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Clone play log sent once "
                    "(same logger ID)."
                )

                return True

            except Exception as e:

                print(
                    "[LOGGER ERROR] Clone logger: "
                    f"{type(e).__name__}: {e}"
                )

                return False

        # =================================================
        # CASE 2
        # CLONE LOGGER ONLY
        # =================================================

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
                    "[LOGGER] Clone logger sent."
                )

            except Exception as e:

                print(
                    "[LOGGER ERROR] Clone logger: "
                    f"{type(e).__name__}: {e}"
                )

        # =================================================
        # MAIN LOGGER
        # ONLY IF IDS ARE DIFFERENT
        # =================================================

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
                    "[LOGGER] Main clone logger sent."
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

async def bot_start_logs(
    client=None,
):

    """
    Main bot start hone par LOGGER_ID me
    sirf ek message.
    """

    try:

        bot_client = client or app

        logger_id = safe_int(
            LOGGER_ID
        )

        if not logger_id:

            print(
                "[LOGGER] LOGGER_ID is not configured."
            )

            return False

        bot = await bot_client.get_me()

        # =================================================
        # DUPLICATE START CHECK
        # =================================================

        start_key = (
            "main_start",
            bot.id,
            logger_id,
        )

        if is_duplicate(
            _START_LOG_CACHE,
            start_key,
        ):

            print(
                "[LOGGER] Duplicate bot-start log skipped."
            )

            return False

        text = f"""
<b>🚀 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

━━━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b>
@{esc(bot.username or "None")}

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

    Aur agar LOGGER_ID alag hai:
    - LOGGER_ID

    SAME ID hone par sirf EK message.
    """

    try:

        bot = await client.get_me()

        clone_logger = safe_int(
            CLONE_LOGGER_ID
        )

        main_logger = safe_int(
            LOGGER_ID
        )

        # =================================================
        # DUPLICATE START CHECK
        # =================================================

        start_key = (
            "clone_start",
            bot.id,
            clone_logger,
            main_logger,
        )

        if is_duplicate(
            _START_LOG_CACHE,
            start_key,
        ):

            print(
                "[LOGGER] Duplicate clone-start "
                "log skipped."
            )

            return False

        text = f"""
<b>🟢 ᴄʟᴏɴᴇ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

━━━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b>
@{esc(bot.username or "None")}

<b>📌 sᴛᴀᴛᴜs:</b>
<code>ONLINE</code>

━━━━━━━━━━━━━━━━━━━━
"""

        # =================================================
        # SAME ID
        # =================================================

        if (
            clone_logger
            and main_logger
            and clone_logger == main_logger
        ):

            try:

                await client.send_message(
                    chat_id=clone_logger,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Clone start log sent once "
                    "(same logger ID)."
                )

                return True

            except Exception as e:

                print(
                    "[LOGGER ERROR] Clone start: "
                    f"{type(e).__name__}: {e}"
                )

                return False

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
                    "[LOGGER ERROR] Clone start: "
                    f"{type(e).__name__}: {e}"
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
                    "[LOGGER ERROR] Main clone start: "
                    f"{type(e).__name__}: {e}"
                )

        return True

    except Exception as e:

        print(
            "[LOGGER ERROR] clone_start_logs: "
            f"{type(e).__name__}: {e}"
        )

        return False
