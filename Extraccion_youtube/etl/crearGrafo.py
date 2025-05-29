"""Este módulo crearemos el Grafo en Neo4j."""
import json
from neo4j import GraphDatabase, basic_auth

# Neo4j Config
NEO4J_URI = "neo4j+s://74cd2897.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "_8BdZrptPmyUOb_ucZPl1fMPNKPX_jj6HLEQrPc0W58"  
NEO4J_DB = "neo4j"

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

def insertar_similitudes_en_neo4j(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    with driver.session(database=NEO4J_DB) as session:
        for entry in data:
            session.run("""
                MERGE (v1:Video {video_id: $id1})
                MERGE (v2:Video {video_id: $id2})
                MERGE (v1)-[r:SIMILAR_A]->(v2)
                SET r.similitud = $similitud
            """, id1=entry["videoId_1"], id2=entry["videoId_2"], similitud=entry["similitud"])
