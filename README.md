# Telegram Music Bot

A simple Telegram bot that behaves like an early MP3 player. Upload audio files, build a library, and play them with automatic progression and manual controls.

## Features

- 📤 Upload audio files (MP3, WAV, etc.) to build your library
- 📋 List all uploaded files with `/list`
- ▶️ Auto-play tracks sequentially with `/play` (with pause/resume/next controls)
- 🔀 Play random tracks with `/shuffle`
- ⏸️ Pause/Resume playback
- ▶️ Skip to next track manually
- 💾 In-memory storage (resets on restart)

## Setup

### 1. Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Install Dependencies

Using `uv` (recommended):
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

Or using `pip`:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Bot Token

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```
BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

You should see:
```
Starting bot...
```

## Usage

1. **Start the bot**: Send `/start` to your bot
2. **Upload audio**: Send any audio file (MP3, WAV, etc.) to the bot
3. **List files**: Use `/list` to see all uploaded tracks
4. **Play**: Use `/play` to start automatic playback
   - Tracks play automatically one after another
   - Use "⏸️ Pause" to pause playback
   - Use "▶️ Resume" to resume
   - Use "▶️ Next" to skip to the next track
5. **Shuffle**: Use `/shuffle` to play a random track
   - Use "🔀 Shuffle Next" to get another random track
6. **Stop**: Use `/stop` to stop playback completely

## Commands

- `/start` - Show welcome message and help
- `/list` - List all uploaded audio files
- `/play` - Start automatic playback from the beginning
- `/shuffle` - Play a random track
- `/stop` - Stop playback

## Deploy to Railway (Cloud Hosting)

Deploy your bot to Railway so it runs 24/7 without your computer:

### 1. Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/iriver-2k25.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign up/login
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository (`iriver-2k25`)
5. Railway will auto-detect Python and start deploying

### 3. Set Environment Variable

1. In your Railway project, go to **"Variables"** tab
2. Click **"New Variable"**
3. Name: `BOT_TOKEN`
4. Value: Your Telegram bot token (from BotFather)
5. Click **"Add"**

### 4. Deploy

Railway will automatically:
- Install dependencies from `requirements.txt`
- Run `python bot.py` (via Procfile)
- Keep your bot running 24/7

### 5. Monitor

- Check **"Deployments"** tab for build logs
- Check **"Metrics"** for resource usage
- Your bot will restart automatically if it crashes

**Note:** Railway free tier includes $5 credit monthly. For a simple bot, this is usually enough.

## Architecture

- **Language**: Python 3.8+
- **Framework**: aiogram 3.x
- **Storage**: In-memory list (resets on restart)
- **File handling**: Uses Telegram `file_id` (no re-uploading)

## Future Extensions (Not Implemented)

The code is structured to easily add:
- Metadata reading (ID3 tags)
- Automatic metadata lookup
- Tagging system
- Search functionality
- Persistent storage (SQLite)

## Troubleshooting

**Bot doesn't respond:**
- Check that `BOT_TOKEN` is set correctly in `.env`
- Make sure the bot is running (check console output)

**Audio files not playing:**
- Ensure files are valid audio formats
- Check bot logs for error messages

**Playback issues:**
- Use `/stop` to reset playback state
- Restart the bot if needed

## License

MIT

