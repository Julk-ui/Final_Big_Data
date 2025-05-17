import yt_dlp

url = "https://www.youtube.com/@Cconstitucional"

ydl_opts = {
    "quiet": False,  # Para ver más detalles
    "extract_flat": True,
    "force_generic_extractor": True,
    "skip_download": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    print(f"\n✅ Canal: {info.get('title', 'Sin título')}")
    print(f"🎥 Videos encontrados: {len(info.get('entries', []))}")
    for entry in info["entries"][:5]:
        print(f" - {entry['title']} ({entry['id']})")
