from neo4j import GraphDatabase

# Datos de conexión (usa variables de entorno en producción)
NEO4J_URI = "neo4j+s://74cd2897.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "_8BdZrptPmyUOb_ucZPl1fMPNKPX_jj6HLEQrPc0W58"
NEO4J_DATABASE = "neo4j"

# Crear el driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def verificar_conexion_neo4j():
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("RETURN 1 AS test")
            valor = result.single()["test"]
            print("✅ Conexión a Neo4j exitosa:", valor)
            return True
    except Exception as e:
        print("❌ Error de conexión a Neo4j:", e)
        return False

# Ejecutar prueba
if __name__ == "__main__":
    verificar_conexion_neo4j()
