from pymongo import MongoClient

MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Youtube_database"
COLLECTION_NAME = "subtitulos"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("✅ Conectado a MongoDB")
    print("Número de documentos:", collection.count_documents({}))
except Exception as e:
    print("❌ Error al conectar a MongoDB:")
    print(e)

#Prueba de Conexion