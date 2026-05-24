import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    
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
                await msg.reply_text(f"📝 {title}\n\n{clean[:3000]}")
            else:
                await msg.reply_text(f"❌ Bu videoda subtitle yo'q\n🎬 {title}")
        except Exception as e:
            await msg.reply_text(f"❌ Xatolik: {str(e)}")
    
    else:
        await msg.reply_text(
            "👋 Salom!\n\n"
            "🎬 YouTube link yuboring → so'zlarini yozaman\n"
            "🎵 Qo'shiq topish funksiyasi tez qo'shiladi!"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))
app.run_polling()
