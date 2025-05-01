import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from tqdm import tqdm


def get_video_list(channel_url: str) -> List[Dict]:
    """Devuelve una lista de videos del canal con título, ID y duración."""
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return [
            {
                "video_id": entry["id"],
                "titulo": entry["title"],
                "url": f"https://www.youtube.com/watch?v={entry['id']}",
                "longitud": entry.get("duration", 0),
            }
            for entry in info.get("entries", [])
            if entry.get("ie_key") == "Youtube"
        ]


def extract_subtitles(video_id: str, language: str = "es") -> List[Dict]:
    """Extrae subtítulos del video en formato requerido."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return [
            {
                "text": item["text"],
                "start": item["start"],
                "duration": item["duration"],
            }
            for item in transcript
        ]
    except (TranscriptsDisabled, NoTranscriptFound):
        return []


def process_video(video: Dict) -> Dict:
    """Extrae subtítulos e incorpora metadatos."""
    transcript = extract_subtitles(video["video_id"])
    return {
        "video_id": video["video_id"],
        "titulo": video["titulo"],
        "url": video["url"],
        "longitud": video["longitud"],
        "texto": transcript,
        "fecha_descarga": datetime.today().strftime("%Y-%m-%d"),
    }


def extract_all_videos(channel_url: str, max_threads: int = 10) -> List[Dict]:
    """Extrae la información de todos los videos del canal con paralelismo."""
    videos = get_video_list(channel_url)
    processed_videos = []

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(process_video, video): video for video in videos}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Procesando videos"):
            result = future.result()
            if result["texto"]:  # Guardamos solo si hay subtítulos
                processed_videos.append(result)

    return processed_videos