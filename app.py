# import modules
from datetime import datetime
from flask import Flask, request, jsonify
import sqlite3
import threading
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file
load_dotenv()

# create flask app
app = Flask(__name__)

# Define constants
YOUTUBE_API_KEYS = os.getenv("YOUTUBE_API_KEY").split(
    ","
)  # Retrieve YouTube API keys from environment variable
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"
DB_NAME = "videos.db"
TABLE_NAME = "videos"
TABLE_SCHEMA = "(video_id TEXT PRIMARY KEY, title TEXT, description TEXT, published_at TEXT, thumbnail_url TEXT)"
SEARCH_QUERY = "cricket"
INTERVAL = 10  # seconds

# Global variables
current_api_key_index = 0


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
    api_key_index = 0
    valid = False
    last_request_time = datetime.utcnow()

    while not valid and api_key_index < len(YOUTUBE_API_KEYS):
        try:
            api_key = YOUTUBE_API_KEYS[api_key_index]
            youtube = build("youtube", "v3", developerKey=api_key)
            req = youtube.search().list(
                q=SEARCH_QUERY,
                part="snippet",
                order="date",
                maxResults=50,
                publishedAfter=(
                    last_request_time.replace(microsecond=0).isoformat() + "Z"
                ),
            )
            res = req.execute()
            print(res)
            valid = True
        except HttpError as err:
            print(err)
            code = err.resp.status
            if not (code == 400 or code == 403):
                break
            else:
                print('api_key_index updated...')
                api_key_index += 1

    if valid:
        # Process the response and store in the database
        for item in res["items"]:
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
    print("in schedule_fetch_and_store_videos...")
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
    cursor.execute(
        f"SELECT * FROM {TABLE_NAME} ORDER BY published_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    rows = cursor.fetchall()
    conn.close()
    video_data = [
        dict(
            zip(
                ["video_id", "title", "description", "published_at", "thumbnail_url"],
                row,
            )
        )
        for row in rows
    ]
    return jsonify(video_data)


# Initialize database and start scheduler
create_table_if_not_exists()
schedule_fetch_and_store_videos()

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
