from neo4j import GraphDatabase, basic_auth

# Tus credenciales
uri = "neo4j+s://75905f35.databases.neo4j.io"
user = "neo4j"
password = "gXRnVMtlUXW-L1BjZz6R0QDE3XyRul7tvtttVooG3tU"
database = "neo4j"

# Intentar conexión
driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

try:
    with driver.session(database=database) as session:
        result = session.run("RETURN 1 AS test")
        print("✅ Conexión exitosa:", result.single()["test"])
except Exception as e:
    print("❌ Error al conectar:", e)
finally:
    driver.close()

