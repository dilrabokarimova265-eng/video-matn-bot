import logging
import yt_dlp
from shazamio import Shazam
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    
    # YouTube link
    if msg.text and ("youtube.com" in msg.text or "youtu.be" in msg.text):
        await msg.reply_text("⏳ Video yuklanmoqda, biroz kuting...")
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['uz', 'ru', 'en'],
                'skip_download': True,
                'outtmpl': '/tmp/%(id)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(msg.text, download=True)
                title = info.get('title', 'Noma\'lum')
                
            sub_file = None
            for lang in ['uz', 'ru', 'en']:
                path = f"/tmp/{info['id']}.{lang}.vtt"
                if os.path.exists(path):
                    sub_file = path
                    break
            
            if sub_file:
                with open(sub_file, 'r') as f:
                    text = f.read()
                clean = '\n'.join([l for l in text.split('\n') 
                                  if l.strip() and '-->' not in l 
                                  and 'WEBVTT' not in l])
                await msg.reply_text(f"📝 *{title}*\n\n{clean[:3000]}", 
                                    parse_mode='Markdown')
            else:
                await msg.reply_text(f"❌ Bu videoda subtitle yo'q\n🎬 {title}")
        except Exception as e:
            await msg.reply_text(f"❌ Xatolik: {str(e)}")
    
    # Audio - qo'shiq topish
    elif msg.audio or msg.voice:
        await msg.reply_text("🎵 Qo'shiq aniqlanmoqda...")
        try:
            file = await context.bot.get_file(
                msg.audio.file_id if msg.audio else msg.voice.file_id
            )
            path = "/tmp/audio_file"
            await file.download_to_drive(path)
            
            shazam = Shazam()
            result = await shazam.recognize(path)
            
            if 'track' in result:
                track = result['track']
                title = track.get('title', 'Noma\'lum')
                artist = track.get('subtitle', 'Noma\'lum')
                await msg.reply_text(f"🎵 *{title}*\n👤 {artist}", 
                                    parse_mode='Markdown')
            else:
                await msg.reply_text("❌ Qo'shiq topilmadi")
        except Exception as e:
            await msg.reply_text(f"❌ Xatolik: {str(e)}")
    
    else:
        await msg.reply_text(
            "👋 Salom! Men nima qila olaman:\n\n"
            "🎬 YouTube link yuboring → so'zlarini yozaman\n"
            "🎵 Audio/ovoz yuboring → qo'shiqni topaman"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))
app.run_polling()
