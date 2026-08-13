from pyrogram.enums import ParseMode

from PritiMusic import app
from config import LOGGER_ID, CLONE_LOGGER_ID


# =========================================================
# SAFE HELPERS
# =========================================================

def get_user_text(user):
    if not user:
        return "Unknown"

    try:
        name = user.mention
    except Exception:
        name = user.first_name or "Unknown"

    username = f"@{user.username}" if user.username else "No Username"

    return f"{name} ({username}) [`{user.id}`]"


def get_chat_text(chat):
    if not chat:
        return "Unknown"

    title = chat.title or chat.first_name or "Unknown"

    if chat.username:
        link = f"https://t.me/{chat.username}"
    else:
        link = "Private Group"

    return (
        f"<b>{title}</b> "
        f"<code>{chat.id}</code>\n"
        f"<b>Link:</b> {link}"
    )


async def get_query(message):
    try:
        if message.text:
            parts = message.text.split(None, 1)

            if len(parts) > 1:
                return parts[1][:1000]

        if message.caption:
            parts = message.caption.split(None, 1)

            if len(parts) > 1:
                return parts[1][:1000]

    except Exception:
        pass

    return "Link / File / Reply"


# =========================================================
# MAIN BOT PLAY LOGGER
# =========================================================

async def play_logs(message, streamtype="Unknown"):
    """
    Main bot ke play logs LOGGER_ID me bhejta hai.

    IMPORTANT:
    Is function me is_on_off(2) ka dependency hata diya gaya hai,
    taaki logger database setting ki wajah se silently OFF na ho.
    """

    try:
        if not LOGGER_ID:
            print("[LOGGER] LOGGER_ID is not configured.")
            return

        # Logger group me same message dobara log na ho
        if message.chat and message.chat.id == LOGGER_ID:
            return

        query = await get_query(message)

        user_text = get_user_text(
            message.from_user
        )

        chat_text = get_chat_text(
            message.chat
        )

        bot = await app.get_me()

        logger_text = f"""
<b>🎵 {bot.mention} ᴘʟᴀʏ ʟᴏɢ</b>

━━━━━━━━━━━━━━━━━━

<b>👤 ᴜsᴇʀ:</b>
{user_text}

<b>🎶 ǫᴜᴇʀʏ:</b>
<code>{query}</code>

<b>📡 sᴏᴜʀᴄᴇ:</b>
<code>{streamtype}</code>

<b>👥 ᴄʜᴀᴛ:</b>
{chat_text}

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}
<code>{bot.id}</code>

━━━━━━━━━━━━━━━━━━
"""

        await app.send_message(
            chat_id=LOGGER_ID,
            text=logger_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        print(
            f"[LOGGER] Play log sent successfully: "
            f"{message.chat.id if message.chat else 'Unknown'}"
        )

    except Exception as e:
        print(
            f"[LOGGER ERROR] play_logs: "
            f"{type(e).__name__}: {e}"
        )


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

    1. Clone logger me
    2. Main LOGGER_ID me
    """

    try:
        bot = await client.get_me()

        if not bot_mention:
            bot_mention = bot.mention

        query = await get_query(message)

        user_text = get_user_text(
            message.from_user
        )

        chat_text = get_chat_text(
            message.chat
        )

        # -------------------------------------------------
        # Clone Logger
        # -------------------------------------------------

        target_clone_logger = (
            clone_logger_id
            or CLONE_LOGGER_ID
        )

        if target_clone_logger:

            clone_text = f"""
<b>🎵 ᴄʟᴏɴᴇ ʙᴏᴛ ᴘʟᴀʏ ʟᴏɢ</b>

━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot_mention}
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀ:</b>
{user_text}

<b>🎶 ǫᴜᴇʀʏ:</b>
<code>{query}</code>

<b>📡 sᴏᴜʀᴄᴇ:</b>
<code>{streamtype}</code>

<b>👥 ᴄʜᴀᴛ:</b>
{chat_text}

━━━━━━━━━━━━━━━━━━
"""

            try:
                await client.send_message(
                    chat_id=int(target_clone_logger),
                    text=clone_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Clone logger message sent."
                )

            except Exception as e:
                print(
                    "[LOGGER ERROR] Clone logger: "
                    f"{type(e).__name__}: {e}"
                )

        # -------------------------------------------------
        # Main Logger
        # -------------------------------------------------

        if LOGGER_ID:

            main_text = f"""
<b>🤖 ᴄʟᴏɴᴇ ʙᴏᴛ ᴘʟᴀʏ</b>

━━━━━━━━━━━━━━━━━━

<b>🤖 ᴄʟᴏɴᴇ:</b>
{bot_mention}
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀ:</b>
{user_text}

<b>🎶 ǫᴜᴇʀʏ:</b>
<code>{query}</code>

<b>📡 sᴏᴜʀᴄᴇ:</b>
<code>{streamtype}</code>

<b>👥 ᴄʜᴀᴛ:</b>
{chat_text}

━━━━━━━━━━━━━━━━━━
"""

            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=main_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                print(
                    "[LOGGER] Main clone log sent."
                )

            except Exception as e:
                print(
                    "[LOGGER ERROR] Main logger: "
                    f"{type(e).__name__}: {e}"
                )

    except Exception as e:
        print(
            f"[LOGGER ERROR] clone_bot_logs: "
            f"{type(e).__name__}: {e}"
        )


# =========================================================
# BOT START LOGGER
# =========================================================

async def bot_start_logs(client=None):
    """
    Bot start hone par LOGGER_ID me message.
    """

    try:
        bot_client = client or app

        bot = await bot_client.get_me()

        owner_text = "Unknown"

        try:
            if bot.id:
                owner_text = f"Bot ID: <code>{bot.id}</code>"
        except Exception:
            pass

        text = f"""
<b>🚀 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b>
@{bot.username or 'None'}

<b>📌 sᴛᴀᴛᴜs:</b>
<code>ONLINE</code>

{owner_text}

━━━━━━━━━━━━━━━━━━
"""

        await app.send_message(
            chat_id=LOGGER_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        print(
            f"[LOGGER] Bot started log sent: @{bot.username}"
        )

    except Exception as e:
        print(
            f"[LOGGER ERROR] bot_start_logs: "
            f"{type(e).__name__}: {e}"
        )


# =========================================================
# CLONE START LOGGER
# =========================================================

async def clone_start_logs(client):
    """
    Clone bot start hone par CLONE_LOGGER_ID
    aur main LOGGER_ID dono me message.
    """

    try:
        bot = await client.get_me()

        text = f"""
<b>🟢 ᴄʟᴏɴᴇ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

━━━━━━━━━━━━━━━━━━

<b>🤖 ʙᴏᴛ:</b>
{bot.mention}

<b>🆔 ɪᴅ:</b>
<code>{bot.id}</code>

<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b>
@{bot.username or 'None'}

<b>📌 sᴛᴀᴛᴜs:</b>
<code>ONLINE</code>

━━━━━━━━━━━━━━━━━━
"""

        # Clone logger
        if CLONE_LOGGER_ID:

            try:
                await client.send_message(
                    chat_id=CLONE_LOGGER_ID,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                print(
                    f"[LOGGER ERROR] clone start logger: {e}"
                )

        # Main logger
        if LOGGER_ID:

            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                print(
                    f"[LOGGER ERROR] main start logger: {e}"
                )

    except Exception as e:
        print(
            f"[LOGGER ERROR] clone_start_logs: "
            f"{type(e).__name__}: {e}"
    )
