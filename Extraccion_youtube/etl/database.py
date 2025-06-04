"""Este módulo proporciona la funcionalidad para cargar videos extraídos a MongoDB."""

from typing import Any, Dict, List
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError

# MongoDB
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#MONGO_URI = "mongodb+srv://msalazarp:Bigdata1@bigdata.bokez.mongodb.net/?retryWrites=true&w=majority&appName=BigData"
DB_NAME = "Youtube_database"
COLLECTION_NAME = "subtitulos"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Neo4j
NEO4J_URI = "neo4j+s://74cd2897.databases.neo4j.io"
NEO4J_USER = "neo4j" 
NEO4J_PASSWORD = "_8BdZrptPmyUOb_ucZPl1fMPNKPX_jj6HLEQrPc0W58"  
NEO4J_DB = "neo4j"  

class DatabaseHandler:
    def __init__(self):
        self.collection = collection
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

        # ✅ Crear índice de texto si no existe
        if "titulo_text_index" not in self.collection.index_information():
            self.collection.create_index([("titulo", "text")], name="titulo_text_index")
    
    def insert_many_videos(self, videos: List[Dict[str, Any]]) -> int:
        if not videos:
            return 0

        count = 0
        for video in videos:
            try:
                if not self.collection.find_one({"video_id": video["video_id"]}):
                    self.collection.insert_one(video)
                    self.insert_video_neo4j(video)
                    count += 1
            except (PyMongoError, Neo4jError) as e:
                print(f"⚠️ Error al insertar {video.get('video_id')}: {e}")
        return count

    def insert_video_neo4j(self, video: Dict[str, Any]) -> None:
        query = """
        MERGE (v:Video {video_id: $video_id})
        SET v.title = $title,
            v.channel = $channel,
            v.description = $description,
            v.date = $date
        """
        params = {
            "video_id": video.get("video_id"),
            "title": video.get("title"),
            "channel": video.get("channel"),
            "description": video.get("description"),
            "date": video.get("date")
        }

        with self.neo4j_driver.session(database=NEO4J_DB) as session:
            session.run(query, **params)

    def remove_all(self) -> int:
        try:
            result = self.collection.delete_many({})
            # Opcional: Borrar también en Neo4j
            with self.neo4j_driver.session(database=NEO4J_DB) as session:
                session.run("MATCH (v:Video) DETACH DELETE v")
            return result.deleted_count
        except Exception as e:
            raise RuntimeError(f"Error al eliminar documentos: {e}")
