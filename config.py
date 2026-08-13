import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


# =========================================================
# BASIC CONFIG
# =========================================================

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")

BOT_TOKEN = getenv("BOT_TOKEN", "")

# FIXED:
# getenv("8761277273") was wrong.
BOT_ID = int(getenv("BOT_ID", "8761277273"))

OWNER_ID = int(getenv("OWNER_ID", "0"))
OWNER_USERNAME = getenv("OWNER_USERNAME", "ll_Weynki_ll")

BOT_USERNAME = getenv("BOT_USERNAME", "Anu_QTbot")
BOT_NAME = getenv("BOT_NAME", "ᴀɴᴜ ᴍᴜꜱɪᴄ")

ASSUSERNAME = getenv("ASSUSERNAME", "musicxanu")

BOT_LINK = getenv(
    "BOT_LINK",
    "https://t.me/Anu_QTbot?start=_tgr_NbOtAJ8xMjI1"
)


# =========================================================
# DATABASE
# =========================================================

MONGO_DB_URI = getenv("MONGO_DB_URI", "")


# =========================================================
# YOUTUBE / DOWNLOAD API
# =========================================================

YTPROXY_URL = getenv(
    "YTPROXY_URL",
    "https://api.shrutibots.site"
)

YT_API_KEY = getenv(
    "YT_API_KEY",
    "ShrutiBotsD6gRJJjTOq2FtGoxgSx6"
)


# =========================================================
# LOGGER
# =========================================================

LOGGER_ID = int(
    getenv(
        "LOGGER_ID",
        "-1004463869572"
    )
)

CLONE_LOGGER_ID = int(
    getenv(
        "CLONE_LOGGER_ID",
        "-1004463869572"
    )
)

# Backward compatibility
CLONE_LOGGER = CLONE_LOGGER_ID


# =========================================================
# HEROKU
# =========================================================

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")


# =========================================================
# GITHUB / UPSTREAM
# =========================================================

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Krishna-The-Fucker/clone-music-"
)

UPSTREAM_BRANCH = getenv(
    "UPSTREAM_BRANCH",
    "main"
)

GIT_TOKEN = getenv("GIT_TOKEN", "")


# =========================================================
# SUPPORT
# =========================================================

SUPPORT_CHANNEL = getenv(
    "SUPPORT_CHANNEL",
    "https://t.me/Wynk_offical"
)

SUPPORT_CHAT = getenv(
    "SUPPORT_CHAT",
    "https://t.me/Wynk_support"
)

GITHUB = getenv(
    "GITHUB",
    "https://files.catbox.moe/tfbzn8.mp4"
)


# =========================================================
# ASSISTANT
# =========================================================

AUTO_LEAVING_ASSISTANT = getenv(
    "AUTO_LEAVING_ASSISTANT",
    "False"
)

AUTO_LEAVE_ASSISTANT_TIME = int(
    getenv("ASSISTANT_LEAVE_TIME", "9000")
)


# =========================================================
# DOWNLOAD LIMITS
# =========================================================

SONG_DOWNLOAD_DURATION = int(
    getenv("SONG_DOWNLOAD_DURATION", "9999999")
)

SONG_DOWNLOAD_DURATION_LIMIT = int(
    getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999")
)


# =========================================================
# SPOTIFY
# =========================================================

SPOTIFY_CLIENT_ID = getenv(
    "SPOTIFY_CLIENT_ID",
    "1c21247d714244ddbb09925dac565aed"
)

SPOTIFY_CLIENT_SECRET = getenv(
    "SPOTIFY_CLIENT_SECRET",
    "709e1a2969664491b58200860623ef19"
)


# =========================================================
# PLAYLIST
# =========================================================

PLAYLIST_FETCH_LIMIT = int(
    getenv("PLAYLIST_FETCH_LIMIT", "25")
)

PLAYLIST_ID = int(
    getenv("PLAYLIST_ID", "-1001980154960")
)


# =========================================================
# TELEGRAM FILE SIZE
# =========================================================

TG_AUDIO_FILESIZE_LIMIT = int(
    getenv(
        "TG_AUDIO_FILESIZE_LIMIT",
        "5242880000"
    )
)

TG_VIDEO_FILESIZE_LIMIT = int(
    getenv(
        "TG_VIDEO_FILESIZE_LIMIT",
        "5242880000"
    )
)


# =========================================================
# STRING SESSIONS
# =========================================================

STRING1 = getenv(
    "STRING_SESSION",
    ""
)

STRING2 = getenv(
    "STRING_SESSION2",
    None
)


# =========================================================
# DATABASE / RUNTIME STATES
# =========================================================

BANNED_USERS = filters.user()

adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


# =========================================================
# IMAGE URL HELPER
# =========================================================

def image_list(value):
    """
    Convert environment image value into a clean list.

    Example:
        "url1 url2 url3"
        -> ["url1", "url2", "url3"]
    """

    if not value:
        return []

    return [
        x.strip()
        for x in str(value).split()
        if x.strip()
    ]


def image_url(value, default):
    """
    Return a single image URL.

    Used where Pyrogram expects a string,
    not a list.
    """

    urls = image_list(value)

    if urls:
        return urls[0]

    return default


# =========================================================
# IMAGE CONFIG
# =========================================================

START_IMG_URL = image_list(
    getenv(
        "START_IMG_URL",
        "https://files.catbox.moe/ozq6o4.jpg"
    )
)

HELP_IMG_URL = image_list(
    getenv(
        "HELP_IMG_URL",
        "https://files.catbox.moe/sji2bj.jpg"
    )
)

PING_IMG_URL = image_list(
    getenv(
        "PING_IMG_URL",
        "https://files.catbox.moe/3zi42m.jpg"
    )
)

PLAYLIST_IMG_URL = image_list(
    getenv(
        "PLAYLIST_IMG_URL",
        "https://i.ibb.co/gL3ykkyh/play-music.jpg"
    )
)

STATS_IMG_URL = image_list(
    getenv(
        "STATS_IMG_URL",
        "https://i.ibb.co/pBqPtFYn/statistics.jpg"
    )
)

TELEGRAM_AUDIO_URL = image_list(
    getenv(
        "TELEGRAM_AUDIO_URL",
        "https://i.ibb.co/gL3ykkyh/play-music.jpg"
    )
)

TELEGRAM_VIDEO_URL = image_list(
    getenv(
        "TELEGRAM_VIDEO_URL",
        "https://i.ibb.co/gL3ykkyh/play-music.jpg"
    )
)

STREAM_IMG_URL = image_list(
    getenv(
        "STREAM_IMG_URL",
        "https://i.ibb.co/0VKCS20y/stream.jpg"
    )
)

SOUNCLOUD_IMG_URL = image_list(
    getenv(
        "SOUNCLOUD_IMG_URL",
        "https://i.ibb.co/S4sPf3q8/soundcloud.jpg"
    )
)

YOUTUBE_IMG_URL = image_list(
    getenv(
        "YOUTUBE_IMG_URL",
        "https://i.ibb.co/xShkBVBK/youtube.jpg"
    )
)

SPOTIFY_ARTIST_IMG_URL = image_list(
    getenv(
        "SPOTIFY_ARTIST_IMG_URL",
        "https://i.ibb.co/XZfMS8Db/spotify.jpg"
    )
)

SPOTIFY_ALBUM_IMG_URL = image_list(
    getenv(
        "SPOTIFY_ALBUM_IMG_URL",
        "https://i.ibb.co/XZfMS8Db/spotify.jpg"
    )
)

SPOTIFY_PLAYLIST_IMG_URL = image_list(
    getenv(
        "SPOTIFY_PLAYLIST_IMG_URL",
        "https://i.ibb.co/XZfMS8Db/spotify.jpg"
    )
)


# =========================================================
# SINGLE IMAGE VARIABLES
# =========================================================
# These are useful for code that expects a string directly.

START_IMG = (
    START_IMG_URL[0]
    if START_IMG_URL
    else "https://files.catbox.moe/ozq6o4.jpg"
)

HELP_IMG = (
    HELP_IMG_URL[0]
    if HELP_IMG_URL
    else "https://files.catbox.moe/sji2bj.jpg"
)

PING_IMG = (
    PING_IMG_URL[0]
    if PING_IMG_URL
    else "https://files.catbox.moe/3zi42m.jpg"
)

PLAYLIST_IMG = (
    PLAYLIST_IMG_URL[0]
    if PLAYLIST_IMG_URL
    else "https://i.ibb.co/gL3ykkyh/play-music.jpg"
)

STATS_IMG = (
    STATS_IMG_URL[0]
    if STATS_IMG_URL
    else "https://i.ibb.co/pBqPtFYn/statistics.jpg"
)

STREAM_IMG = (
    STREAM_IMG_URL[0]
    if STREAM_IMG_URL
    else "https://i.ibb.co/0VKCS20y/stream.jpg"
)


# =========================================================
# TIME
# =========================================================

def time_to_seconds(time):
    value = str(time)

    try:
        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(
                reversed(value.split(":"))
            )
        )
    except (ValueError, TypeError):
        return 0


DURATION_LIMIT_MIN = int(
    getenv("DURATION_LIMIT", "17000")
)

DURATION_LIMIT = int(
    time_to_seconds(
        f"{DURATION_LIMIT_MIN}:00"
    )
)


# =========================================================
# URL VALIDATION
# =========================================================

if SUPPORT_CHANNEL and not re.match(
    r"^(?:http|https)://",
    SUPPORT_CHANNEL
):
    raise SystemExit(
        "[ERROR] - SUPPORT_CHANNEL url must start with https://"
    )


if SUPPORT_CHAT and not re.match(
    r"^(?:http|https)://",
    SUPPORT_CHAT
):
    raise SystemExit(
        "[ERROR] - SUPPORT_CHAT url must start with https://"
    )


# =========================================================
# EMOJIS
# =========================================================

CMBOT = [
    "💞", "🥂", "🔍", "🧪", "⚡️", "🔥", "🦋", "🎩",
    "🌈", "🍷", "🥃", "🥤", "🕊️", "💌", "🧨", "✨",
    "💥", "💯", "🌟", "⚡️", "❤️", "😍", "🥰", "😘",
    "😂", "🤣", "😱", "😡", "👏", "🙏", "🎉", "🎊",
    "🎶", "🎵", "🎧", "🎸", "🎹", "🥁", "🎺", "🎷",
    "🔥", "⚡️", "💫", "🌙", "☀️", "🌈", "❄️", "🌸",
    "🌺", "🌹", "🦋", "🕊️", "🐍", "🐯", "🦁", "🐺",
    "🐉", "🦅", "🦄", "🐎"
]


# =========================================================
# MESSAGE EFFECTS
# =========================================================

EFFECT_ID = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]
