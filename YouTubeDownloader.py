import os
import re
import requests
import shutil
import yt_dlp

def is_valid_url(url):
    """Checks if the URL is valid and reachable."""
    try:
        # Send a HEAD request to the URL to check its status without downloading the content
        response = requests.head(url, allow_redirects=True)  
        if response.status_code == 200:
            return True  # URL is valid
        else:
            print(f"Error: Received a {response.status_code} status code.")  # Print the error code if not 200
            return False  # URL is invalid
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")  # Print the error if there was an issue with the request
        return False  # Error in the request

def check_ffmpeg():
    """Checks if FFmpeg is installed on the system."""
    return shutil.which("ffmpeg") is not None  # Returns True if FFmpeg is found, False otherwise

def get_download_path(audio_only):
    """Determines the appropriate path for saving the download based on the file type (audio or video)."""
    home = os.path.expanduser("~")  # Get the user's home directory
    music_path = os.path.join(home, "Musica")  # Path for audio files
    video_path = os.path.join(home, "Video")  # Path for video files
    desktop_path = os.path.join(home, "Desktop")  # Default path (Desktop)
    
    if audio_only and os.path.exists(music_path):
        return music_path  # Return music path if audio-only mode is selected
    elif not audio_only and os.path.exists(video_path):
        return video_path  # Return video path if video mode is selected
    else:
        return desktop_path  # Default to desktop path if neither path exists
    
def is_playlist(url):
    """Checks if the URL is part of a YouTube playlist by looking for the 'list=' parameter in the URL."""
    return bool(re.search(r'(youtube\.com|youtu\.be)/.*(list=)', url))

def download_video(url, audio_only=False):
    """Downloads the video or audio from the provided URL."""
    path = get_download_path(audio_only)  # Get the download path
    options = {
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),  # Set the output template for the file
        'extractor_args': {
            'generic': ['impersonate']  # Add argument to impersonate the browser
        }
    }

    # If the URL is a playlist, ask the user if they want to download the entire playlist
    if is_playlist(url):
        mode = input("This link is part of a playlist. Do I have to download the entire playlist?(y/n): ").strip().lower()
        playlist = mode in ["y", "yes"]
        if playlist:
            options.update({
                'noplaylist': False  # Allow downloading the playlist if the link is a playlist
            })
        else:
            options.update({
                'playlist_items': '1',  # Download only the first video of the playlist
                'noplaylist': True  # Disable playlist mode
            })
    
    # If audio-only mode is selected
    if audio_only:
        if check_ffmpeg():
            options.update({
                'format': 'bestaudio',  # Select the best audio format
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract audio
                    'preferredcodec': 'mp3',  # Set MP3 as the preferred audio format
                    'preferredquality': '192',  # Set the audio quality to 192 kbps
                }]
            })
            print("Downloading and converting to MP3...")
        else:
            options.update({
                'format': 'bestaudio',  # Select the best audio format
                'postprocessors': []  # Disable the audio conversion if FFmpeg is not found
            })
            print("FFmpeg not found. Downloading audio without converting...")
    else:
        options['format'] = 'best'  # Select the best video format
        print("Downloading video...")

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])  # Start the download process
        print(f"Download completed! File saved to: {path}")  # Inform the user that the download is complete
    except Exception as e:
        print(f"Error: {e}")  # Print the error if the download fails

if __name__ == "__main__":
    video_url = input("Enter the URL of the YouTube video: ")  # Ask for the video URL
    if is_valid_url(video_url) == True:  # Check if the URL is valid
        mode = input("Do you want to download only the audio? (y/n): ").strip().lower()  # Ask if the user wants audio only
        audio_only = mode in ["y", "yes"]  # Set audio_only to True if the user wants audio only
        download_video(video_url, audio_only)  # Call the download function
    else:
        print("Error in the link or in the connection.")  # Inform the user if the URL is invalid or there is a connection error
