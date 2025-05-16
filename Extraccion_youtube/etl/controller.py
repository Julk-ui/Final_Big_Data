"""Controlador para cargar videos extraídos en MongoDB."""

from typing import List, Dict
from Extraccion_youtube.etl.database import DatabaseHandler


class VideoController:
    def __init__(self):
        self.db = DatabaseHandler()

    def insertar_videos(self, lista_videos: List[Dict]) -> int:
        """
        Inserta videos con subtítulos o con error identificable en MongoDB.
        Filtra los que tengan estado 'ok', 'sin_subtitulos' o 'error_general'.
        """
        videos_validos = [
            v for v in lista_videos
            if v.get("estado") in ("ok", "sin_subtitulos", "error_general")
        ]

        cantidad = self.db.insert_many_videos(videos_validos)
        print(f"✅ {cantidad} videos insertados en MongoDB.")
        return cantidad
