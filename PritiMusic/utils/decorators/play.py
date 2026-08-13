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

from config import (
    PLAYLIST_IMG_URL,
    SUPPORT_CHAT,
    adminlist,
)

from strings import get_string


links = {}
clinks = {}


def get_image(value):
    """
    Pyrogram ko single image string return karta hai.
    """

    if isinstance(value, list):
        return value[0] if value else None

    return value


def PlayWrapper(command):

    async def wrapper(client, message):

        language = await get_lang(message.chat.id)
        _ = get_string(language)

        # =================================================
        # SENDER CHAT CHECK
        # =================================================

        if message.sender_chat:

            upl = InlineKeyboardMarkup(
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
                reply_markup=upl,
            )

        # =================================================
        # MAINTENANCE
        # =================================================

        if await is_maintenance() is False:

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
        # DELETE COMMAND
        # =================================================

        try:
            await message.delete()
        except Exception:
            pass

        # =================================================
        # TELEGRAM MEDIA
        # =================================================

        audio_telegram = None
        video_telegram = None

        if message.reply_to_message:

            audio_telegram = (
                message.reply_to_message.audio
                or message.reply_to_message.voice
            )

            video_telegram = (
                message.reply_to_message.video
                or message.reply_to_message.document
            )

        # =================================================
        # YOUTUBE URL
        # =================================================

        url = await YouTube.url(message)

        # =================================================
        # NO INPUT
        # =================================================

        if (
            audio_telegram is None
            and video_telegram is None
            and url is None
        ):

            if len(message.command) < 2:

                if "stream" in message.command:
                    return await message.reply_text(
                        _["str_1"]
                    )

                buttons = botplaylist_markup(_)

                playlist_image = get_image(
                    PLAYLIST_IMG_URL
                )

                if not playlist_image:
                    return await message.reply_text(
                        _["play_18"],
                        reply_markup=InlineKeyboardMarkup(
                            buttons
                        ),
                    )

                return await message.reply_photo(
                    photo=playlist_image,
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(
                        buttons
                    ),
                )

        # =================================================
        # CHAT MODE
        # =================================================

        if message.command[0][0] == "c":

            chat_id = await get_cmode(
                message.chat.id
            )

            if chat_id is None:
                return await message.reply_text(
                    _["setting_7"]
                )

            try:
                chat = await app.get_chat(chat_id)
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

        playmode = await get_playmode(
            message.chat.id
        )

        playty = await get_playtype(
            message.chat.id
        )

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

                if message.from_user.id not in admins:
                    return await message.reply_text(
                        _["play_4"]
                    )

        # =================================================
        # VIDEO FLAG
        # =================================================

        command_text = message.text or ""

        first_command = (
            message.command[0]
            if message.command
            else ""
        )

        if first_command.startswith("v"):

            video = True

        elif "-v" in command_text:

            video = True

        elif (
            len(message.command) > 1
            and message.command[1].lower() == "v"
        ):

            video = True

        else:

            video = None

        # =================================================
        # FORCE PLAY
        # =================================================

        last_command = (
            message.command[0]
            if message.command
            else ""
        )

        if last_command.endswith("e"):

            if not await is_active_chat(chat_id):
                return await message.reply_text(
                    _["play_16"]
                )

            fplay = True

        else:

            fplay = None

        # =================================================
        # ASSISTANT JOIN
        # =================================================

        if not await is_active_chat(chat_id):

            userbot = await get_assistant(chat_id)

            if not userbot:
                return await message.reply_text(
                    _["call_1"]
                )

            try:

                try:

                    get = await app.get_chat_member(
                        chat_id,
                        userbot.id,
                    )

                except ChatAdminRequired:

                    return await message.reply_text(
                        _["call_1"]
                    )

                if get.status in (
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
                                        text="๏ 𝗨ɴʙᴀɴ 𝗔ssɪsᴛᴀɴᴛ ๏",
                                        callback_data="unban_assistant",
                                    )
                                ]
                            ]
                        ),
                    )

            except UserNotParticipant:

                # =========================================
                # GET INVITE LINK
                # =========================================

                if chat_id in links:

                    invitelink = links[chat_id]

                else:

                    if message.chat.username:

                        invitelink = (
                            message.chat.username
                        )

                        try:
                            await userbot.resolve_peer(
                                invitelink
                            )
                        except Exception:
                            pass

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

                # =========================================
                # NORMALIZE INVITE LINK
                # =========================================

                if invitelink.startswith(
                    "https://t.me/+"
                ):

                    invitelink = invitelink.replace(
                        "https://t.me/+",
                        "https://t.me/joinchat/",
                    )

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

                except UserAlreadyParticipant:

                    pass

                except Exception as e:

                    return await message.reply_text(
                        _["call_3"].format(
                            app.mention,
                            type(e).__name__,
                        )
                    )

                links[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(
                        chat_id
                    )
                except Exception:
                    pass

        # =================================================
        # CALL ACTUAL PLAY FUNCTION
        # =================================================

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

    return wrapper
