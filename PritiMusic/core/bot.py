from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config

from ..logging import LOGGER


class Lucky(Client):

    def __init__(self):

        LOGGER(__name__).info(
            "Starting Bot..."
        )

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

        self.id = self.me.id

        self.name = (
            self.me.first_name
            + " "
            + (self.me.last_name or "")
        )

        self.username = self.me.username
        self.mention = self.me.mention

        # =================================================
        # LOGGER CHECK
        # =================================================

        try:

            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<b>🚀 ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n"
                    f"<b>🤖 ʙᴏᴛ:</b> {self.mention}\n"
                    f"<b>🆔 ɪᴅ:</b> "
                    f"<code>{self.id}</code>\n"
                    f"<b>👤 ɴᴀᴍᴇ:</b> "
                    f"{self.name}\n"
                    f"<b>🔗 ᴜsᴇʀɴᴀᴍᴇ:</b> "
                    f"@{self.username or 'None'}\n\n"
                    f"<b>📌 sᴛᴀᴛᴜs:</b> "
                    f"<code>ONLINE</code>"
                ),
                disable_web_page_preview=True,
            )

        except (
            errors.ChannelInvalid,
            errors.PeerIdInvalid,
            errors.ChatIdInvalid,
        ):

            LOGGER(__name__).error(
                "Bot cannot access LOGGER_ID. "
                "Make sure the bot is inside the logger group/channel."
            )

            raise

        except Exception as ex:

            LOGGER(__name__).error(
                "Logger send failed: "
                f"{type(ex).__name__}: {ex}"
            )

            raise

        # =================================================
        # LOGGER ADMIN CHECK
        # =================================================

        try:

            member = await self.get_chat_member(
                config.LOGGER_ID,
                self.id,
            )

            if member.status != ChatMemberStatus.ADMINISTRATOR:

                LOGGER(__name__).error(
                    "Bot must be ADMIN in LOGGER_ID."
                )

                raise RuntimeError(
                    "Bot is not admin in LOGGER_ID."
                )

        except Exception as ex:

            LOGGER(__name__).error(
                "LOGGER_ID permission check failed: "
                f"{type(ex).__name__}: {ex}"
            )

            raise

        LOGGER(__name__).info(
            f"Music Bot Started as {self.name}"
        )

    async def stop(self):

        LOGGER(__name__).info(
            "Stopping Music Bot..."
        )

        await super().stop()
