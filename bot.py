from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup
import os

API_ID = int(os.getenv("API_ID", "27064328"))
API_HASH = os.getenv("API_HASH", "7be1392c2fe5ebf4fc3228706fbfb504")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8150594528:AAGbXespT08i6YU0d4_ZUDIkF_8m9NsKNik")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_terabox_video_links(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        video_tags = soup.find_all("source")

        video_links = {}
        for video in video_tags:
            quality = video.get("label") or "Unknown Quality"
            video_links[quality] = video.get("src", "")

        return video_links if video_links else None

    return None

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text(
        "👋 Welcome to **Terabox Video Downloader Bot**!\n"
        "Send a Terabox video link, and I'll fetch it for you.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support", url="https://t.me/TonyStarkBotzXSupport")]
        ])
    )

@app.on_message(filters.command("download"))
def download_video(client, message):
    if len(message.command) < 2:
        message.reply_text(
            "❌ Please provide a Terabox video URL.\n"
            "**Example:**\n"
            "`/download <link>`"
        )
        return

    url = message.command[1]
    message.reply_text("🔍 Fetching available video qualities...")

    video_links = get_terabox_video_links(url)

    if video_links:
        buttons = [
            [InlineKeyboardButton(f"Download {quality}", url=link)]
            for quality, link in video_links.items() if link
        ]
        message.reply_text("🎥 Select a video quality:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        message.reply_text("❌ Failed to extract video links. Please check the URL.")

app.run()