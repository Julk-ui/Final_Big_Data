from pymongo import MongoClient

# Conexión a tu base de datos MongoDB
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["Youtube_database"]
collection = db["subtitulos"]

collection.drop_index("nombre_video_text_subtitulos.texto_text")
collection.create_index(
    [("titulo", "text"), ("texto.text", "text")],
    name="titulo_texto_text_index"
)