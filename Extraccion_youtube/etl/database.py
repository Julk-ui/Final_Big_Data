"""This module provides the RP To-Do database functionality with MongoDB."""

from typing import Any, Dict, List, NamedTuple
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from etl.extract import extract_audio
from etl.extract import regex
from etl.extract import extract_youtube_subtitles

from etl import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS

# Configuración de MongoDB
MONGO_URI = "mongodb+srv://msalazarp:Bigdata1@bigdata.bokez.mongodb.net/?retryWrites=true&w=majority&appName=BigData"
DB_NAME = "ETL_database"
COLLECTION_NAME = "audios"

# Conexión global a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


class DBResponse(NamedTuple):
    todo_list: List[Dict[str, Any]]
    error: int


class DatabaseHandler:
    def __init__(self):
        """Inicializa la conexión a MongoDB."""
        self.collection = collection  # Usa la conexión global

    def add_audio(self, path: str) -> Dict[str, Any]:
        """Extrae texto de un audio y lo guarda en MongoDB."""
        if not path:
            raise ValueError("El 'path' no puede estar vacío.")

        # Extraer texto del audio
        text = extract_youtube_subtitles(path)

        # Verificar si el texto se extrajo correctamente
        if not text or "No se pudo reconocer el audio" in text:
            raise RuntimeError(
                "El audio no contiene texto válido o no pudo ser procesado."
            )

        document = {"Path": path, "Text": text, "BigData": regex(text)}
        try:
            result = self.collection.insert_one(document)
            document["_id"] = str(result.inserted_id)
            return document
        except PyMongoError as e:
            raise RuntimeError(f"Error al insertar en MongoDB: {e}")

    def get_audios(self) -> List[Dict[str, Any]]:
        """Obtener todos los audios de MongoDB con todos los campos."""
        try:
            return list(self.collection.find({}, {"_id": 0}))  # No devolver `_id`
        except PyMongoError as e:
            raise RuntimeError(f"Error al leer desde MongoDB: {e}")

    def remove_all(self) -> int:
        """Elimina todos los documentos de la colección."""
        try:
            result = self.collection.delete_many({})
            return result.deleted_count  # Número de documentos eliminados
        except PyMongoError as e:
            raise RuntimeError(f"Error al eliminar documentos: {e}")
