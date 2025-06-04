"""Este módulo crea el grafo en Neo4j a partir de un archivo de similitudes."""

import json
import os
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError

# Neo4j Config
#NEO4J_URI = "neo4j+s://74cd2897.databases.neo4j.io"
#NEO4J_USER = "neo4j"
#NEO4J_PASSWORD = "_8BdZrptPmyUOb_ucZPl1fMPNKPX_jj6HLEQrPc0W58"  
#NEO4J_DB = "neo4j"

NEO4J_URI="neo4j+s://75905f35.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="gXRnVMtlUXW-L1BjZz6R0QDE3XyRul7tvtttVooG3tU"
NEO4J_DB="neo4j"

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

def insertar_similitudes_en_neo4j(json_path: str):
    """Inserta relaciones de similitud en Neo4j desde un archivo JSON."""

    if not os.path.exists(json_path):
        print(f"❌ El archivo no existe: {json_path}")
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el archivo JSON: {e}")
        return

    if isinstance(data, dict):
        data = [data]

    print(f"📦 Insertando {len(data)} relaciones en Neo4j...")

    try:
        with driver.session(database=NEO4J_DB) as session:
            for entry in data:
                try:
                    session.run("""
                        MERGE (v1:Video {video_id: $id1})
                        MERGE (v2:Video {video_id: $id2})
                        MERGE (v1)-[r:SIMILAR_A]->(v2)
                        SET r.similitud = $similitud
                    """, id1=entry["videoId_1"], id2=entry["videoId_2"], similitud=entry["similitud"])
                    print(f"✅ Relación insertada: {entry['videoId_1']} ↔ {entry['videoId_2']}")
                    print(f"Inserción: {entry['videoId_1']} → {entry['videoId_2']} ({entry['similitud']})")
                except Neo4jError as e:
                    print(f"⚠️ Error con relación {entry['videoId_1']} - {entry['videoId_2']}: {e}")

    except Exception as e:
        print(f"❌ Error general de conexión o transacción en Neo4j: {e}")
    finally:
        driver.close()
        print("🔒 Conexión a Neo4j cerrada.")

if __name__ == "__main__":
    insertar_similitudes_en_neo4j("Similitud.json")