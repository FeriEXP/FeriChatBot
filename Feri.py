import re
import requests
import traceback
from asyncio import get_running_loop
from io import BytesIO
from googletrans import Translator
from gtts import gTTS
from time import time
from datetime import datetime
from asyncio import gather, get_event_loop, sleep
from aiohttp import ClientSession
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters, idle
from Python_ARQ import ARQ
from config import (
    bot_token,
    ARQ_API_KEY,
    LANGUAGE,
    api_id,
    api_hash,
    ARQ_API_BASE_URL,
    BOT_USERNAME,
    KONTOL,
    MEMEK,
)

print("[INFO]: INITIALIZING BOT CLIENT ...")
feri = Client(
    ":memory:",
    bot_token=bot_token,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
)

bot_id = int(bot_token.split(":")[0])
arq = None
print("[INFO]: INITIALIZING ...")


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1)
)


def convert(text):
    audio = BytesIO()
    i = Translator().translate(text, dest="id")
    lang = i.src
    tts = gTTS(text, lang=lang)
    audio.name = lang + ".mp3"
    tts.write_to_fp(audio)
    return audio


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}"
                         .format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


async def lunaQuery(query: str, user_id: int):
    query = (
        query
        if LANGUAGE == "en"
        else (await arq.translate(query, "en")).result.translatedText
    )
    resp = (await arq.luna(query, user_id)).result
    return (
        resp
        if LANGUAGE == "en"
        else (
            await arq.translate(resp, LANGUAGE)
        ).result.translatedText
    )


async def type_and_send(message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    query = message.text.strip()
    await message._client.send_chat_action(chat_id, "typing")
    response, _ = await gather(lunaQuery(query, user_id), sleep(2))
    if "Luna" in response:
        responsee = response.replace("Luna", f"{KONTOL}")
    else:
        responsee = response
    if "Aco" in responsee:
        responsess = responsee.replace("Aco", f"{KONTOL}")
    else:
        responsess = responsee
    if "Who is feri?" in responsess:
        responsess2 = responsess.replace("Who is feri?", "Kontol bapak kau pecah")
    else:
        responsess2 = responsess
    await message.reply_text(responsess2)
    await message._client.send_chat_action(chat_id, "cancel")


@feri.on_message(filters.command(["start", f"start@{BOT_USERNAME}"]) & ~filters.edited)
async def start(_, message):
    await feri.send_chat_action(message.chat.id, "typing")
    await sleep(2)
    await message.reply_text("**Assalamualaikum**")


@feri.on_message(
    ~filters.private
    & filters.text
    & ~filters.command(["start", f"start@{BOT_USERNAME}"])
    & ~filters.edited,
    group=69,
)
async def chat(_, message: Message):
    if message.reply_to_message:
        if not message.reply_to_message.from_user:
            return
        from_user_id = message.reply_to_message.from_user.id
        if from_user_id != bot_id:
            return
    else:
        match = re.search(
            "[.|\n]{0,}feri[.|\n]{0,}",
            message.text.strip(),
            flags=re.IGNORECASE,
        )
        if not match:
            return
    await type_and_send(message)


@feri.on_message(filters.private & ~filters.command(["start", f"start@{BOT_USERNAME}"]) & ~filters.edited)
async def chatpm(_, message):
    if not message.text:
        await message.reply_text("Ufff... ignoring ....")
        return
    await type_and_send(message)


@feri.on_message(filters.command(["asupan", f"asupan@{BOT_USERNAME}"]))
async def asupan(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/asupan/ptl").json()
        results = f"{resp['url']}"
        return await client.send_video(message.chat.id, video=results)
    except Exception:
        await message.reply_text("`404 asupan videos not found:v`")


@feri.on_message(filters.command(["wibu", f"wibu@{BOT_USERNAME}"]))
async def wibu(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/asupan/wibu").json()
        results = f"{resp['url']}"
        return await client.send_video(message.chat.id, video=results)
    except Exception:
        await message.reply_text("`404 wibu not found:v`")


@feri.on_message(filters.command(["truth", f"truth@{BOT_USERNAME}"]))
async def truth(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/truth").json()
        results = f"{resp['message']}"
        return await message.reply_text(results)
    except Exception:
        await message.reply_text("something went wrong...")


@feri.on_message(filters.command(["dare", f"dare@{BOT_USERNAME}"]))
async def dare(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/dare").json()
        results = f"{resp['message']}"
        return await message.reply_text(results)
    except Exception:
        await message.reply_text("something went wrong...")


@feri.on_message(filters.command(["chika", f"chika@{BOT_USERNAME}"]))
async def chika(client, message):
    try:
        resp = requests.get("https://api-tede.herokuapp.com/api/chika").json()
        results = f"{resp['url']}"
        return await client.send_video(message.chat.id, video=results)
    except Exception:
        await message.reply_text("`404 chika videos not found`")


@feri.on_message(filters.command(["tts", f"tts@{BOT_USERNAME}"]))
async def text_to_speech(_, message: Message):
    memek = message.reply_to_message
    if not memek:
        await message.reply_text("`reply to some text...`")
        return
    try:
        m = await message.reply_text("`processing...`")
        tempek = message.reply_to_message.text
        loop = get_running_loop()
        audio = await loop.run_in_executor(None, convert, tempek)
        await message.reply_audio(audio)
        await m.delete()
        audio.close()
    except Exception as e:
        await m.edit(str(e))
        es = traceback.format_exc()
        print(es)


@feri.on_message(filters.command(["alive", f"alive@{BOT_USERNAME}"]))
async def alive(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    CROOT = f"{MEMEK}"
    await client.send_video(message.chat.id, CROOT,
caption=f"""**༄ Holla I'm [{KONTOL}](https://t.me/{BOT_USERNAME})**
༄ **I'm Working Properly**
༄ **Bot : 8.0 LATEST**
༄ **My Master : [Feri](https://t.me/xflicks)**
༄ **Service Uptime : `{uptime}`**
**Thanks For Using Me ♥️**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ꜱᴏᴜʀᴄᴇ", url="https://github.com/FeriEXP/FeriChatBot"
                    ),
                    InlineKeyboardButton(
                        "ꜱᴜᴘᴘᴏʀᴛ", url="https://t.me/anossupport"
                    )
                ]
            ]
        )
    )


async def main():
    global arq
    session = ClientSession()
    arq = ARQ(ARQ_API_BASE_URL, ARQ_API_KEY, session)

    await feri.start()
    print(
        """
    -----------------
  | Chatbot Started! |
    -----------------
"""
    )
    await idle()


loop = get_event_loop()
loop.run_until_complete(main())
