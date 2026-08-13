from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode

import config

from ..logging import LOGGER


class Lucky(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")

        super().__init__(
            name="PritiMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()

        # =====================================================
        # BOT INFORMATION
        # =====================================================

        self.id = self.me.id
        self.name = (
            self.me.first_name
            + (" " + self.me.last_name if self.me.last_name else "")
        )
        self.username = self.me.username
        self.mention = self.me.mention

        # =====================================================
        # LOGGER GROUP
        # =====================================================

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=f"""
<b>🟢 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>

<b>🤖 ʙᴏᴛ :</b> {self.mention}

<b>🆔 ɪᴅ :</b>
<code>{self.id}</code>

<b>👤 ɴᴀᴍᴇ :</b>
{self.name}

<b>🔗 ᴜsᴇʀɴᴀᴍᴇ :</b>
@{self.username or "None"}
""",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        except (
            errors.ChannelInvalid,
            errors.PeerIdInvalid,
            errors.ChatIdInvalid,
        ):
            LOGGER(__name__).error(
                "❌ LOGGER_ID is invalid or bot cannot access "
                "the logger group/channel."
            )

        except errors.ChatAdminRequired:
            LOGGER(__name__).error(
                "❌ Bot needs admin permission in LOGGER_ID."
            )

        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ Failed to send bot-start log: "
                f"{type(ex).__name__}: {ex}"
            )

        # =====================================================
        # CHECK LOGGER ADMIN STATUS
        # =====================================================

        try:
            member = await self.get_chat_member(
                config.LOGGER_ID,
                self.id,
            )

            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "❌ Bot is NOT ADMIN in LOGGER_ID. "
                    "Please promote the bot as administrator."
                )
            else:
                LOGGER(__name__).info(
                    "✅ Bot is admin in LOGGER_ID."
                )

        except Exception as ex:
            LOGGER(__name__).error(
                f"❌ LOGGER permission check failed: "
                f"{type(ex).__name__}: {ex}"
            )

        # =====================================================
        # START SUCCESS
        # =====================================================

        LOGGER(__name__).info(
            f"🎵 Music Bot Started as {self.name}"
        )

    async def stop(self):
        LOGGER(__name__).info(
            f"Stopping Music Bot: {self.name}"
        )

        await super().stop()
