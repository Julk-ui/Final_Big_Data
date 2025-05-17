from Extraccion_youtube.etl.extract import extract_all_videos_batching
import json

# URL del canal oficial
channel_url = "https://www.youtube.com/@Cconstitucional/videos"

# Ejecutar la recolección de los primeros videos del canal
if __name__ == "__main__":
    print("Iniciando extracción...")
    resultados = extract_all_videos_batching(channel_url, max_threads=4, batch_size=100)

    print(f"\nSe extrajeron {len(resultados)} videos con subtítulos.")
    for video in resultados[:3]:  # Mostrar solo los primeros 3 resultados
        print("\n--- Video ---")
        print(f"Título: {video['titulo']}")
        print(f"ID: {video['video_id']}")
        print(f"Transcripción (primeras líneas):")
        for line in video["texto"][:5]:
            print(f"  > {line['text']} [{line['start']}s]")

# Guardar resultados en archivo JSON
output_path = "videos_extraidos.jsonl"
with open(output_path, "w", encoding="utf-8") as f:
    for video in resultados:
        f.write(json.dumps(video, ensure_ascii=False) + "\n")

print(f"\nSe guardaron los resultados en: {output_path}")

# 🥽 PRUEBA DE BLOQUEO DE YOUTUBE.

#from youtube_transcript_api import YouTubeTranscriptApi

#try:
#    print(YouTubeTranscriptApi.get_transcript("nSeFx6ZId6k", languages=["es"]))
#except Exception as e:
#    print("Aún estás bloqueado:", e)

