# Video Dashboard

This Flask project fetches and stores YouTube videos based on a specified search query. It provides an API to retrieve and display the stored videos with sorting and filtering options. The project utilizes the YouTube Data API for fetching videos and stores them in a SQLite database.

## Getting Started

### Prerequisites

- Python 3.x
- [pip](https://pip.pypa.io/en/stable/installation/)
- [YouTube API Key](https://developers.google.com/youtube/v3/getting-started)

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/adi611/yt-api.git
    cd yt-api
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate # On Unix/Linux
    # or
    venv\Scripts\activate # On Windows
3. Install dependencies
    ```bash
    pip install -r requirements.txt
4. Set up your environment variables:
    - Create a `.env` file in the project root.
    - Add your YouTube API keys (separated by commas if multiple) to the `.env` file:
        ```bash
        YOUTUBE_API_KEYS=API_KEY_1,API_KEY_2,...
### Usage

1. Run the Flask application:

    ```bash
    python app.py
2. Access the Video Dashboard at http://127.0.0.1:5000/dashboard
3. Making GET Requests:

    You can manually make GET requests to the API using tools like curl or Postman.
    - Example using `curl``:

        ```bash
        curl -X GET "http://127.0.0.1:5000/videos?page=1&per_page=10&sort=published_at&filter=your_keyword" -H "Content-Type: application/json"
    - Example using Postman:
        - Set the request URL to http://127.0.0.1:5000/videos.
        - Choose the GET method.
        - Add parameters (page, per_page, sort, filter) in the request.
### Features

- Fetches and stores YouTube videos asynchronously with scheduled tasks.
- Provides an API for retrieving stored videos with sorting and filtering options.
- Basic video dashboard with sorting by published date, title, and description.
- Pagination for video display.
### Project Structure
- `app.py`: Main Flask application.
- `templates/dashboard.html`: HTML template for the video dashboard.
- `videos.db`: SQLite database file for storing videos.
- `requirements.txt`: List of Python dependencies.