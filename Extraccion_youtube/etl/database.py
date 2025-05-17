"""Este módulo proporciona la funcionalidad para cargar videos extraídos a MongoDB."""

from typing import Any, Dict, List
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Configuración de MongoDB
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#MONGO_URI = "mongodb+srv://msalazarp:Bigdata1@bigdata.bokez.mongodb.net/?retryWrites=true&w=majority&appName=BigData"
DB_NAME = "Youtube_database"
COLLECTION_NAME = "subtitulos"

# Conexión global a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


class DatabaseHandler:
    def __init__(self):
        """Inicializa la conexión a MongoDB."""
        self.collection = collection

    def insert_many_videos(self, videos: List[Dict[str, Any]]) -> int:
        """
        Inserta múltiples documentos de videos en MongoDB.
        Evita duplicados usando 'video_id' como campo clave.
        """
        if not videos:
            return 0

        count = 0
        for video in videos:
            try:
                if not self.collection.find_one({"video_id": video["video_id"]}):
                    self.collection.insert_one(video)
                    count += 1
            except PyMongoError as e:
                print(f"⚠️ Error al insertar {video.get('video_id')}: {e}")
                continue

        return count
    
    def remove_all(self) -> int:
        """Elimina todos los documentos de la colección de videos."""
        try:
            result = self.collection.delete_many({})
            return result.deleted_count
        except Exception as e:
            raise RuntimeError(f"Error al eliminar documentos: {e}")

