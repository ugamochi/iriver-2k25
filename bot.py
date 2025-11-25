import asyncio
import logging
import os
import random
import signal
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

library = []
playback_state = {
    "is_playing": False,
    "current_index": 0,
    "task": None,
    "last_message": None
}


def get_playback_keyboard(is_playing: bool) -> InlineKeyboardMarkup:
    buttons = []
    if is_playing:
        buttons.append(InlineKeyboardButton(text="⏸️ Pause", callback_data="pause"))
    else:
        buttons.append(InlineKeyboardButton(text="▶️ Resume", callback_data="resume"))
    buttons.append(InlineKeyboardButton(text="▶️ Next", callback_data="next"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_shuffle_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔀 Shuffle Next", callback_data="shuffle_next")
    ]])


async def send_track(message: Message, index: int, is_shuffle: bool = False):
    if not library:
        await message.answer("Library is empty. Upload some audio files first!")
        return
    
    if is_shuffle:
        index = random.randint(0, len(library) - 1)
    
    track = library[index]
    track_name = track["original_name"]
    
    try:
        await message.answer_audio(
            audio=track["file_id"],
            caption=f"🎵 {track_name}"
        )
        return index
    except Exception as e:
        logger.error(f"Error sending track: {e}")
        await message.answer(f"Error playing track: {e}")
        return None


async def auto_play_loop(message: Message):
    while playback_state["is_playing"] and library:
        if not playback_state["is_playing"]:
            break
            
        index = playback_state["current_index"]
        track = library[index]
        track_name = track["original_name"]
        duration = track.get("duration", 30)
        
        try:
            sent_msg = await message.answer_audio(
                audio=track["file_id"],
                caption=f"🎵 {track_name}",
                reply_markup=get_playback_keyboard(is_playing=True)
            )
            playback_state["last_message"] = sent_msg
            
            wait_time = max(duration + 2, 5)
            elapsed = 0
            check_interval = 1
            
            while elapsed < wait_time and playback_state["is_playing"]:
                await asyncio.sleep(check_interval)
                elapsed += check_interval
            
            if playback_state["is_playing"]:
                playback_state["current_index"] = (playback_state["current_index"] + 1) % len(library)
            else:
                if sent_msg:
                    try:
                        await sent_msg.edit_reply_markup(reply_markup=get_playback_keyboard(is_playing=False))
                    except:
                        pass
                break
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in auto_play_loop: {e}")
            # If error occurs, wait a bit and try next track
            await asyncio.sleep(2)
            playback_state["current_index"] = (playback_state["current_index"] + 1) % len(library)
            continue


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🎵 Welcome to the Music Bot!\n\n"
        "Upload audio files to add them to your library.\n\n"
        "Commands:\n"
        "/list - List all uploaded files\n"
        "/play - Start playing tracks automatically\n"
        "/shuffle - Play a random track\n"
        "/stop - Stop playback\n"
        "/clear - Clear library\n"
        "/source - View source code on GitHub"
    )


@dp.message(Command("clear"))
async def cmd_clear(message: Message):
    if not library:
        await message.answer("Library is already empty.")
        return
        
    if playback_state["is_playing"]:
        playback_state["is_playing"] = False
        if playback_state["task"]:
            playback_state["task"].cancel()
            playback_state["task"] = None
            
    library.clear()
    playback_state["current_index"] = 0
    await message.answer("🗑️ Library cleared.")


@dp.message(Command("list"))
async def cmd_list(message: Message):
    if not library:
        await message.answer("Library is empty. Upload some audio files first!")
        return
    
    track_list = "\n".join([
        f"{i+1}. {track['original_name']}"
        for i, track in enumerate(library)
    ])
    await message.answer(f"📋 Your library ({len(library)} tracks):\n\n{track_list}")


@dp.message(Command("play"))
async def cmd_play(message: Message):
    if not library:
        await message.answer("Library is empty. Upload some audio files first!")
        return
    
    if playback_state["is_playing"]:
        await message.answer("Playback is already running. Use /stop to stop it first.")
        return
    
    if playback_state["task"] and not playback_state["task"].done():
        playback_state["task"].cancel()
    
    playback_state["is_playing"] = True
    playback_state["current_index"] = 0
    playback_state["task"] = asyncio.create_task(auto_play_loop(message))


@dp.message(Command("shuffle"))
async def cmd_shuffle(message: Message):
    if not library:
        await message.answer("Library is empty. Upload some audio files first!")
        return
    
    index = await send_track(message, 0, is_shuffle=True)
    if index is not None:
        await message.answer(
            "🎲 Random track selected!",
            reply_markup=get_shuffle_keyboard()
        )


@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    if playback_state["is_playing"]:
        playback_state["is_playing"] = False
        if playback_state["task"]:
            playback_state["task"].cancel()
            playback_state["task"] = None
        await message.answer("⏹️ Playback stopped.")
    else:
        await message.answer("Playback is not running.")


@dp.message(Command("source"))
async def cmd_source(message: Message):
    await message.answer(
        "📦 Source Code\n\n"
        "This bot is open source and hosted on GitHub:\n"
        "https://github.com/ugamochi/iriver-2k25\n\n"
        "Deployed on Fly.io (free tier)."
    )


@dp.callback_query(F.data == "pause")
async def callback_pause(callback: CallbackQuery):
    if playback_state["is_playing"]:
        playback_state["is_playing"] = False
        await callback.answer("⏸️ Playback paused")
        try:
            await callback.message.edit_reply_markup(reply_markup=get_playback_keyboard(is_playing=False))
        except:
            if playback_state["last_message"]:
                try:
                    await playback_state["last_message"].edit_reply_markup(reply_markup=get_playback_keyboard(is_playing=False))
                except:
                    pass
    else:
        await callback.answer("Already paused")


@dp.callback_query(F.data == "resume")
async def callback_resume(callback: CallbackQuery):
    if not playback_state["is_playing"]:
        playback_state["is_playing"] = True
        await callback.answer("▶️ Playback resumed")
        try:
            await callback.message.edit_reply_markup(reply_markup=get_playback_keyboard(is_playing=True))
        except:
            if playback_state["last_message"]:
                try:
                    await playback_state["last_message"].edit_reply_markup(reply_markup=get_playback_keyboard(is_playing=True))
                except:
                    pass
        
        if not playback_state["task"] or playback_state["task"].done():
            playback_state["task"] = asyncio.create_task(auto_play_loop(callback.message))
    else:
        await callback.answer("Already playing")


@dp.callback_query(F.data == "next")
async def callback_next(callback: CallbackQuery):
    if not library:
        await callback.answer("Library is empty", show_alert=True)
        return
    
    was_playing = playback_state["is_playing"]
    
    if playback_state["task"] and not playback_state["task"].done():
        playback_state["task"].cancel()
        playback_state["task"] = None
    
    playback_state["current_index"] = (playback_state["current_index"]) % len(library)
    index = await send_track(callback.message, playback_state["current_index"], is_shuffle=False)
    
    if index is not None:
        playback_state["current_index"] = (playback_state["current_index"] + 1) % len(library)
        if was_playing:
            playback_state["is_playing"] = True
            playback_state["task"] = asyncio.create_task(auto_play_loop(callback.message))
    
    await callback.answer()


@dp.callback_query(F.data == "shuffle_next")
async def callback_shuffle_next(callback: CallbackQuery):
    if not library:
        await callback.answer("Library is empty", show_alert=True)
        return
    
    index = await send_track(callback.message, 0, is_shuffle=True)
    if index is not None:
        await callback.message.answer(
            "🎲 Random track selected!",
            reply_markup=get_shuffle_keyboard()
        )
    await callback.answer()


@dp.message(F.audio | F.voice | F.document)
async def handle_audio(message: Message):
    file_id = None
    original_name = "Unknown"
    duration = 30
    
    if message.audio:
        file_id = message.audio.file_id
        original_name = message.audio.file_name or message.audio.title or "Unknown"
        duration = message.audio.duration or 30
    elif message.voice:
        file_id = message.voice.file_id
        original_name = "Voice message"
        duration = message.voice.duration or 30
    elif message.document:
        mime_type = message.document.mime_type or ""
        if "audio" in mime_type:
            file_id = message.document.file_id
            original_name = message.document.file_name or "Unknown"
            duration = 30
    
    if file_id:
        track = {
            "file_id": file_id,
            "original_name": original_name,
            "duration": duration
        }
        library.append(track)
        await message.answer(f"✅ Added: {original_name}")
        logger.info(f"Added track: {original_name} (duration: {duration}s, file_id: {file_id[:20]}...)")
    else:
        await message.answer("Please send an audio file (MP3, WAV, etc.)")


async def main():
    logger.info("Starting bot...")
    
    # Handle graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    
    def signal_handler():
        logger.info("Received stop signal")
        stop_event.set()
        
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
        
    # Run polling in background
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    # Wait for stop signal
    await stop_event.wait()
    
    logger.info("Shutting down...")
    if playback_state["task"]:
        playback_state["task"].cancel()
        
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
        
    await bot.session.close()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Bot error: {e}")

