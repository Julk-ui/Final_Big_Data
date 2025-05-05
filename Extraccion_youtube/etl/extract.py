import os
import time
import json
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from tqdm import tqdm
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable


def get_video_list(channel_url: str) -> List[Dict]:
    """Devuelve una lista de videos del canal con título, ID y duración."""
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{channel_url}/videos", download=False)
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

def extract_subtitles(video_id: str, titulo: str = "", language: str = "es") -> List[Dict]:
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    time.sleep(5)  # Controla la tasa de solicitudes
    return [
        {
            "text": item["text"],
            "start": item["start"],
            "duration": item["duration"],
        }
        for item in transcript
    ]

def process_video(video: Dict) -> Dict:
    def try_extract(attempt: int = 1) -> Dict:
        try:
            transcript = extract_subtitles(video["video_id"], video["titulo"])
            estado = "ok" if transcript else "sin_subtitulos"
            detalle_error = ""
        except VideoUnavailable:
            estado = "bloqueo"
            transcript = []
            detalle_error = "Video bloqueado o eliminado"
        except (TranscriptsDisabled, NoTranscriptFound):
            estado = "sin_subtitulos"
            transcript = []
            detalle_error = "No hay subtítulos disponibles"
        except Exception as e:
            if attempt == 1:
                print(f"[⚠️ Error general intento 1] {video['video_id']}. Reintentando en 30s...")
                time.sleep(30)
                return try_extract(attempt=2)
            estado = "error_general"
            transcript = []
            detalle_error = str(e)

        return {
            "video_id": video["video_id"],
            "titulo": video["titulo"],
            "url": video["url"],
            "longitud": video["longitud"],
            "texto": transcript,
            "fecha_descarga": datetime.today().strftime("%Y-%m-%d"),
            "estado": estado,
            "detalle_error": detalle_error
        }

    return try_extract()

def extract_all_videos_batching(channel_url: str, max_threads: int = 3, batch_size: int = 100) -> List[Dict]:
    videos = get_video_list(channel_url)
    processed_videos = []
    batch = []
    batch_index = 0

    os.makedirs("resultados_batches", exist_ok=True)

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(process_video, video): video for video in videos}
        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Procesando videos")):
            try:
                result = future.result()
                batch.append(result)
            except Exception as e:
                print(f"[ERROR] Falló el procesamiento de un video: {e}")
                continue

            # Cuando alcanzamos el tamaño de lote, guardamos
            if len(batch) >= batch_size:
                path = f"resultados_batches/videos_batch_{batch_index}.json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(batch, f, ensure_ascii=False, indent=2)
                print(f"✔ Lote {batch_index} guardado con {len(batch)} videos en {path}")
                batch_index += 1
                processed_videos.extend(batch)
                batch = []  # Reiniciar lote

        # Guardar el último lote incompleto
        if batch:
            path = f"resultados_batches/videos_batch_{batch_index}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(batch, f, ensure_ascii=False, indent=2)
            print(f"✔ Lote {batch_index} guardado con {len(batch)} videos (último lote)")

            processed_videos.extend(batch)

    return processed_videos