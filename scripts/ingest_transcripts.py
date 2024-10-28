import os
import json
from googleapiclient.discovery import build

# Initialize API key
API_KEY = 'AIzaSyChcD4fJyh9zyYkjd9nXkAfN9TuRi4dmQM'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Directory to store transcripts
os.makedirs('transcripts', exist_ok=True)

# Connect to the YouTube API
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_video_ids(playlist_id):
    """Retrieve all video IDs from a YouTube playlist."""
    video_ids = []
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50  # Adjust if needed
    )
    while request:
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        request = youtube.playlistItems().list_next(request, response)
    return video_ids

def download_transcript(video_id):
    """Download and save the transcript for a single video."""
    # (Placeholder for transcript retrieval code; implement here if you have a method for transcript extraction)
    # For now, simulate transcript with placeholder text
    transcript = f"Transcript for video {video_id}..."
    
    # Save the transcript to a file
    with open(f"transcripts/{video_id}.txt", "w") as f:
        f.write(transcript)

def main():
    # Insert the Mind The Game playlist ID here
    playlist_id = "PLp2G5GXjpIZ9833syzfb9m5Z8SJfkjpP7"
    video_ids = get_video_ids(playlist_id)
    
    for video_id in video_ids:
        download_transcript(video_id)
        print(f"Downloaded transcript for video {video_id}")

if __name__ == "__main__":
    main()