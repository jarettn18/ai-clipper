from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from pytube import YouTube
import os
import uuid

from services.whisper_service import transcribe_video
from services.highlight_extractor import extract_highlight_segments
from services.video_utils import clip_video_segments

router = APIRouter()

MEDIA_DIR = "media/"
CLIPS_DIR = "clips/"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

@router.post("/youtube", response_class=HTMLResponse)
async def process_youtube_link(request: Request, youtube_url: str = Form(...)):
    try:
        # Generate unique filename
        video_id = str(uuid.uuid4())
        video_path = os.path.join(MEDIA_DIR, f"{video_id}.mp4")

        # Download the video
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(file_extension="mp4", progressive=True).get_highest_resolution()
        stream.download(output_path=MEDIA_DIR, filename=f"{video_id}.mp4")

        # Transcribe with Whisper
        result = transcribe_video(video_path)

        # Extract highlights (based on keywords)
        highlights = extract_highlight_segments(result)

        # Clip video
        clip_video_segments(video_path, highlights, output_dir=CLIPS_DIR)

        return HTMLResponse(content=f"""
            <h2>Highlights generated!</h2>
            <p>Original Video: {youtube_url}</p>
            <p>{len(highlights)} highlight(s) created.</p>
            <a href="/">Back to Home</a>
        """, status_code=200)

    except Exception as e:
        return HTMLResponse(content=f"<h2>Error:</h2><pre>{e}</pre><a href='/'>Back</a>", status_code=500)
