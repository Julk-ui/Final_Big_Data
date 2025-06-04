"""Este módulo crea nodos y relaciones de similitud en Neo4j, validando previamente en MongoDB."""

import json
from pymongo import MongoClient
from neo4j import GraphDatabase, basic_auth

# === CONFIGURACIÓN MONGODB ===
#MONGO_URI = "mongodb+srv://msalazarp:Bigdata1@bigdata.bokez.mongodb.net/?retryWrites=true&w=majority&appName=BigData"
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB_NAME = "Youtube_database"
#MONGO_DB_NAME = "ETL_database"
MONGO_COLLECTION = "subtitulos"
#MONGO_COLLECTION = "videos"

mongo_client = MongoClient(MONGO_URI)
mongo_collection = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION]

# === CONFIGURACIÓN NEO4J ===
NEO4J_URI = "neo4j+s://75905f35.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "gXRnVMtlUXW-L1BjZz6R0QDE3XyRul7tvtttVooG3tU"
NEO4J_DB = "neo4j"

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

# === FUNCIÓN PRINCIPAL ===
def insertar_similitudes_validando(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    with driver.session(database=NEO4J_DB) as session:
        insertados = 0
        omitidos = 0

        for entry in data:
            id1 = entry.get("videoId_1")
            id2 = entry.get("videoId_2")
            similitud = entry.get("similitud")

            if not id1 or not id2 or similitud is None:
                continue  # Saltar si faltan datos

            # Verificar que ambos videos existen en Mongo
            existe1 = mongo_collection.count_documents({"video_id": id1}) > 0
            existe2 = mongo_collection.count_documents({"video_id": id2}) > 0

            if existe1 and existe2:
                session.run("""
                    MERGE (v1:Video {video_id: $id1})
                    MERGE (v2:Video {video_id: $id2})
                    MERGE (v1)-[r:SIMILAR_A]->(v2)
                    SET r.similitud = $similitud
                """, id1=id1, id2=id2, similitud=similitud)
                insertados += 1
            else:
                omitidos += 1

        print(f"✔ Se insertaron {insertados} relaciones en Neo4j.")
        print(f"❌ Se omitieron {omitidos} pares por no existir en MongoDB.")

# === LLAMADO DE PRUEBA (opcional) ===
#if __name__ == "__main__":
#    insertar_similitudes_validando("Similitud (1).json")
