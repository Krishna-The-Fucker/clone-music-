import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import Playlist


# =========================================================
# CONFIG
# =========================================================

# Supports both the old SHRUTI_* names and the YT_* names
# already present in the project's config/environment.
API_URL = os.environ.get(
    "SHRUTI_API_URL",
    os.environ.get(
        "YTPROXY_URL",
        "https://api.shrutibots.site",
    ),
).rstrip("/")

API_KEY = os.environ.get(
    "SHRUTI_API_KEY",
    os.environ.get(
        "YT_API_KEY",
        "ShrutiBotsD6gRJJjTOq2FtGoxgSx6",
    ),
)

DOWNLOAD_DIR = "downloads"


# =========================================================
# HELPERS
# =========================================================

def time_to_seconds(time):
    if not time:
        return 0

    try:
        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(
                reversed(str(time).split(":"))
            )
        )
    except (TypeError, ValueError):
        return 0


def seconds_to_time(seconds):
    try:
        seconds = int(seconds or 0)
    except (TypeError, ValueError):
        seconds = 0

    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def clean_youtube_url(link: str):
    if not link:
        return link

    link = str(link).strip()

    # Keep only the main YouTube URL when common tracking
    # parameters are present.
    if "&" in link:
        link = link.split("&", 1)[0]

    return link


def extract_video_id(link: str):
    if not link:
        return None

    link = str(link).strip()

    if "youtu.be/" in link:
        video_id = link.split("youtu.be/", 1)[1].split("?", 1)[0]

    elif "youtube.com/watch?v=" in link:
        video_id = link.split("v=", 1)[1].split("&", 1)[0]

    elif "youtube.com/shorts/" in link:
        video_id = link.split("youtube.com/shorts/", 1)[1].split("?", 1)[0]

    else:
        video_id = link

    video_id = video_id.strip()

    if not video_id or len(video_id) < 3:
        return None

    return video_id


def is_youtube_url(link: str):
    if not link:
        return False

    return bool(
        re.search(
            r"(?:youtube\.com|youtu\.be)",
            str(link),
            re.IGNORECASE,
        )
    )


async def yt_dlp_extract(query, options):
    """
    Run yt-dlp outside the asyncio event loop.
    This prevents YouTube extraction from blocking the bot.
    """

    def _extract():
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(
                query,
                download=False,
            )

    return await asyncio.to_thread(_extract)


def first_entry(info):
    if not info:
        return None

    entries = info.get("entries")

    if entries is not None:
        entries = [entry for entry in entries if entry]

        if not entries:
            return None

        return entries[0]

    return info


# =========================================================
# API DOWNLOAD
# =========================================================

async def _api_download(video_id: str, media_type: str, timeout_seconds: int):
    if not video_id:
        return None

    if not API_KEY:
        print(
            "[DOWNLOAD] API key is not configured. "
            "Set SHRUTI_API_KEY or YT_API_KEY."
        )
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    extension = "mp3" if media_type == "audio" else "mp4"

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.{extension}",
    )

    if os.path.exists(file_path):
        try:
            if os.path.getsize(file_path) > 0:
                return file_path
        except OSError:
            pass

        try:
            os.remove(file_path)
        except OSError:
            pass

    try:
        params = {
            "url": video_id,
            "type": media_type,
            "api_key": API_KEY,
        }

        timeout = aiohttp.ClientTimeout(
            total=timeout_seconds
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                f"{API_URL}/download",
                params=params,
            ) as resp:

                if resp.status != 200:
                    print(
                        f"[DOWNLOAD] API returned HTTP {resp.status}"
                    )
                    return None

                with open(file_path, "wb") as file:
                    async for chunk in resp.content.iter_chunked(131072):
                        if chunk:
                            file.write(chunk)

        if (
            os.path.exists(file_path)
            and os.path.getsize(file_path) > 0
        ):
            return file_path

    except Exception as e:
        print(
            f"[DOWNLOAD] API error: "
            f"{type(e).__name__}: {e}"
        )

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass

    return None


async def download_song(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    return await _api_download(
        video_id,
        "audio",
        300,
    )


async def download_video(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    return await _api_download(
        video_id,
        "video",
        600,
    )


# =========================================================
# YOUTUBE API
# =========================================================

class YouTubeAPI:

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    # =====================================================
    # EXISTS
    # =====================================================

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if not link:
            return False

        if videoid:
            link = self.base + str(link)

        return bool(
            re.search(
                self.regex,
                str(link),
                re.IGNORECASE,
            )
        )

    # =====================================================
    # URL FROM TELEGRAM MESSAGE
    # =====================================================

    async def url(
        self,
        message_1: Message,
    ) -> Union[str, None]:

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            if message.entities:
                for entity in message.entities:

                    if entity.type == MessageEntityType.URL:
                        text = (
                            message.text
                            or message.caption
                            or ""
                        )

                        return text[
                            entity.offset:
                            entity.offset + entity.length
                        ]

            if message.caption_entities:
                for entity in message.caption_entities:

                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        return None

    # =====================================================
    # GET INFO
    #
    # FIX:
    # The old code used py_yt.VideosSearch for details.
    # This now uses yt-dlp for YouTube search/details.
    # =====================================================

    async def _get_info(
        self,
        link: str,
        videoid: Union[bool, str] = None,
        limit: int = 1,
    ):

        if not link:
            raise ValueError(
                "Empty YouTube query"
            )

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        if is_youtube_url(link):
            query = link
        else:
            query = f"ytsearch{max(1, int(limit))}:{link}"

        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "nocheckcertificate": True,
        }

        info = await yt_dlp_extract(
            query,
            options,
        )

        if not info:
            raise RuntimeError(
                "YouTube returned an empty response."
            )

        return info

    # =====================================================
    # DETAILS
    # =====================================================

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        try:
            info = await self._get_info(
                link,
                videoid,
                limit=1,
            )

            result = first_entry(info)

            if not result:
                raise RuntimeError(
                    "No YouTube result found."
                )

            title = (
                result.get("title")
                or "Unknown"
            )

            duration_sec = int(
                result.get("duration")
                or 0
            )

            duration_min = seconds_to_time(
                duration_sec
            )

            vidid = (
                result.get("id")
                or extract_video_id(
                    result.get("webpage_url")
                    or result.get("url")
                )
            )

            if not vidid:
                raise RuntimeError(
                    "YouTube video ID not found."
                )

            thumbnail = (
                result.get("thumbnail")
                or f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"
            )

            print(
                f"[YouTube.details] "
                f"{title} | {duration_min} | {vidid}"
            )

            return (
                title,
                duration_min,
                duration_sec,
                thumbnail,
                vidid,
            )

        except Exception as e:
            print(
                f"[YouTube.details] ERROR: "
                f"{type(e).__name__}: {e}"
            )
            raise

    # =====================================================
    # TITLE
    # =====================================================

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        try:
            data = await self.details(
                link,
                videoid,
            )
            return data[0]

        except Exception as e:
            print(
                f"[YouTube.title] ERROR: {e}"
            )
            return None

    # =====================================================
    # DURATION
    # =====================================================

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        try:
            data = await self.details(
                link,
                videoid,
            )
            return data[1]

        except Exception as e:
            print(
                f"[YouTube.duration] ERROR: {e}"
            )
            return None

    # =====================================================
    # THUMBNAIL
    # =====================================================

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        try:
            data = await self.details(
                link,
                videoid,
            )
            return data[3]

        except Exception as e:
            print(
                f"[YouTube.thumbnail] ERROR: {e}"
            )
            return None

    # =====================================================
    # VIDEO
    # =====================================================

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + str(link)

        try:
            downloaded_file = await download_video(
                link
            )

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed."

        except Exception as e:
            print(
                f"[YouTube.video] ERROR: {e}"
            )
            return 0, (
                f"Video download error: {e}"
            )

    # =====================================================
    # PLAYLIST
    # =====================================================

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None,
    ):

        if not link:
            return []

        if videoid:
            link = self.listbase + str(link)

        link = clean_youtube_url(link)

        try:
            plist = await Playlist.get(
                link
            )

        except Exception as e:
            print(
                f"[YouTube.playlist] ERROR: {e}"
            )
            return []

        videos = (
            plist.get("videos")
            or []
        )

        ids = []

        for data in videos[:limit]:

            if not data:
                continue

            vid = data.get("id")

            if not vid:
                continue

            ids.append(vid)

        return ids

    # =====================================================
    # TRACK
    #
    # FIX:
    # Old code used VideosSearch here too.
    # =====================================================

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        try:
            info = await self._get_info(
                link,
                videoid,
                limit=1,
            )

            result = first_entry(info)

            if not result:
                raise RuntimeError(
                    "No YouTube result found."
                )

            title = (
                result.get("title")
                or "Unknown"
            )

            duration_sec = int(
                result.get("duration")
                or 0
            )

            duration_min = seconds_to_time(
                duration_sec
            )

            vidid = (
                result.get("id")
                or extract_video_id(
                    result.get("webpage_url")
                    or result.get("url")
                )
            )

            if not vidid:
                raise RuntimeError(
                    "YouTube video ID not found."
                )

            yturl = (
                result.get("webpage_url")
                or f"{self.base}{vidid}"
            )

            thumbnail = (
                result.get("thumbnail")
                or f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"
            )

            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }

            print(
                f"[YouTube.track] "
                f"{title} | {duration_min} | {vidid}"
            )

            return (
                track_details,
                vidid,
            )

        except Exception as e:
            print(
                f"[YouTube.track] ERROR: "
                f"{type(e).__name__}: {e}"
            )
            raise

    # =====================================================
    # FORMATS
    # =====================================================

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        options = {
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
        }

        try:
            info = await yt_dlp_extract(
                link,
                options,
            )

            formats_available = []

            for fmt in info.get(
                "formats",
                [],
            ):

                try:
                    if (
                        "dash"
                        in str(
                            fmt.get(
                                "format",
                                "",
                            )
                        ).lower()
                    ):
                        continue

                    formats_available.append(
                        {
                            "format": fmt.get(
                                "format"
                            ),
                            "filesize": fmt.get(
                                "filesize"
                            ),
                            "format_id": fmt.get(
                                "format_id"
                            ),
                            "ext": fmt.get(
                                "ext"
                            ),
                            "format_note": fmt.get(
                                "format_note"
                            ),
                            "yturl": link,
                        }
                    )

                except Exception:
                    continue

            return (
                formats_available,
                link,
            )

        except Exception as e:
            print(
                f"[YouTube.formats] ERROR: {e}"
            )
            return [], link

    # =====================================================
    # SLIDER
    # =====================================================

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        try:
            info = await self._get_info(
                link,
                videoid,
                limit=10,
            )

            results = info.get(
                "entries",
                [],
            )

            results = [
                item
                for item in results
                if item
            ]

            if not results:
                raise RuntimeError(
                    "No slider results found."
                )

            try:
                index = int(query_type)
            except (TypeError, ValueError):
                index = 0

            if index < 0 or index >= len(results):
                index = 0

            result = results[index]

            title = (
                result.get("title")
                or "Unknown"
            )

            duration_sec = int(
                result.get("duration")
                or 0
            )

            duration_min = seconds_to_time(
                duration_sec
            )

            vidid = result.get("id")

            if not vidid:
                raise RuntimeError(
                    "Slider video ID not found."
                )

            thumbnail = (
                result.get("thumbnail")
                or f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"
            )

            return (
                title,
                duration_min,
                thumbnail,
                vidid,
            )

        except Exception as e:
            print(
                f"[YouTube.slider] ERROR: {e}"
            )
            raise

    # =====================================================
    # DOWNLOAD
    # =====================================================

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:

        if videoid:
            link = self.base + str(link)

        try:

            if video:
                downloaded_file = await download_video(
                    link
                )
            else:
                downloaded_file = await download_song(
                    link
                )

            if downloaded_file:
                return (
                    downloaded_file,
                    True,
                )

            return (
                None,
                False,
            )

        except Exception as e:
            print(
                f"[YouTube.download] ERROR: {e}"
            )
            return (
                None,
                False,
            )


# =========================================================
# GLOBAL INSTANCE
# =========================================================

YouTube = YouTubeAPI()
