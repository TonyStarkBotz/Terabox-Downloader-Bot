from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup
import os

API_ID = int(os.getenv("API_ID", "YOUR_API_ID"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_terabox_video_links(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        video_tags = soup.find_all("source")

        video_links = {}
        for video in video_tags:
            quality = video.get("label", "Unknown Quality")
            video_links[quality] = video["src"]

        return video_links

    return None

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text(
        "👋 Welcome to **Terabox Video Downloader Bot**!
"
        "Send a Terabox video link, and I'll fetch it for you.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support", url="https://t.me/YourSupportGroup")]
        ])
    )

@app.on_message(filters.command("download"))
def download_video(client, message):
    if len(message.command) < 2:
        message.reply_text("❌ Please provide a Terabox video URL.
Example:
`/download <link>`")
        return

    url = message.command[1]
    message.reply_text("🔍 Fetching available video qualities...")

    video_links = get_terabox_video_links(url)

    if video_links:
        buttons = [
            [InlineKeyboardButton(f"Download {quality}", callback_data=link)]
            for quality, link in video_links.items()
        ]
        message.reply_text("🎥 Select a video quality:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        message.reply_text("❌ Failed to extract video links. Please check the URL.")

@app.on_callback_query()
def button(client, callback_query):
    video_url = callback_query.data
    callback_query.message.reply_text(f"⬇️ Downloading video...
{video_url}")

    video_file = "video.mp4"
    response = requests.get(video_url, stream=True)

    with open(video_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024*1024):
            file.write(chunk)

    callback_query.message.reply_video(video=video_file, caption="📽 Here is your downloaded video!")
    os.remove(video_file)

app.run()
