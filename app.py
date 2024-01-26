# import modules
from flask import Flask, request, jsonify
import requests
import sqlite3
import time
import threading
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# create flask app
app = Flask(__name__)

# Define constants
YOUTUBE_API_KEY = os.getenv(
    "YOUTUBE_API_KEY"
)  # Retrieve YouTube API key from environment variable
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"
DB_NAME = "videos.db"
TABLE_NAME = "videos"
TABLE_SCHEMA = "(video_id TEXT PRIMARY KEY, title TEXT, description TEXT, published_at TEXT, thumbnail_url TEXT)"
SEARCH_QUERY = "cricket"
INTERVAL = 10  # seconds

# Database utility functions
def create_table_if_not_exists():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} {TABLE_SCHEMA}")
    conn.commit()
    conn.close()

def insert_video_data(video_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"INSERT OR IGNORE INTO {TABLE_NAME} VALUES (?,?,?,?,?)", video_data)
    conn.commit()
    conn.close()

def fetch_videos_from_youtube():
    print('in fetch_videos_from_youtube...')
    current_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    search_url = YOUTUBE_BASE_URL + "/search"
    search_params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "type": "video",
        "order": "date",
        "publishedAfter": current_time,
        "q": SEARCH_QUERY
    }
    response = requests.get(search_url, params=search_params)
    if response.status_code == 200:
        data = response.json()
        for item in data["items"]:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            title = snippet["title"]
            description = snippet["description"]
            published_at = snippet["publishedAt"]
            thumbnail_url = snippet["thumbnails"]["default"]["url"]
            video_data = (video_id, title, description, published_at, thumbnail_url)
            insert_video_data(video_data)

# Scheduler utility function
def schedule_fetch_and_store_videos():
    print('in schedule_fetch_and_store_videos...')
    threading.Timer(INTERVAL, schedule_fetch_and_store_videos).start()
    fetch_videos_from_youtube()

# Routes
@app.route("/videos", methods=["GET"])
def get_videos():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page
    limit = per_page
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY published_at DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    video_data = [dict(zip(["video_id", "title", "description", "published_at", "thumbnail_url"], row)) for row in rows]
    return jsonify(video_data)

# Initialize database and start scheduler
create_table_if_not_exists()
schedule_fetch_and_store_videos()

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
