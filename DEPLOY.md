# Railway Deployment Checklist

## Quick Steps

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/iriver-2k25.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python

3. **Set Environment Variable**
   - In Railway project → "Variables" tab
   - Add: `BOT_TOKEN` = `your_token_from_botfather`
   - Bot will auto-restart with new variable

4. **Verify**
   - Check "Deployments" tab for successful build
   - Test bot in Telegram - send `/start`

## Files Included

- ✅ `bot.py` - Main bot code
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Tells Railway how to run the bot
- ✅ `.gitignore` - Excludes .env from git

## Troubleshooting

**Build fails:**
- Check Railway logs in "Deployments" tab
- Ensure `requirements.txt` is correct

**Bot doesn't respond:**
- Verify `BOT_TOKEN` is set in Railway Variables
- Check Railway logs for errors
- Make sure bot is running (green status)

**Bot stops:**
- Railway free tier may have limits
- Check "Metrics" for resource usage
- Bot auto-restarts on crash

