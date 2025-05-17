import streamlit as st
from pymongo import MongoClient, TEXT
from bson.objectid import ObjectId
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# --- Conexión a MongoDB ---
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Youtube_database"
COLLECTION_NAME = "subtitulos"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Crear índice de texto si no existe
collection.create_index([("nombre_video", TEXT), ("subtitulos.texto", TEXT)])

# --- Interfaz Streamlit ---
st.title("Consulta de Subtítulos de Videos en MongoDB")

opcion = st.sidebar.selectbox("Seleccione una acción:", [
    "Consultar por ID de video",
    "Buscar por nombre del video (texto)",
    "Buscar por rango de fechas",
    "Buscar palabra en subtítulos",
    "Similitud entre videos",
    "Red de similitudes"
])

# --- 1. Consultar por ID ---
if opcion == "Consultar por ID de video":
    video_id = st.text_input("Ingrese el ID del video:")
    if video_id:
        video = collection.find_one({"_id": video_id})
        if video:
            st.json(video)
        else:
            st.warning("Video no encontrado.")

# --- 2. Buscar por nombre (texto) ---
elif opcion == "Buscar por nombre del video (texto)":
    texto = st.text_input("Ingrese un texto para buscar en el nombre del video:")
    if texto:
        resultados = collection.find({"$text": {"$search": texto}})
        for video in resultados:
            st.write(f"ID: {video['_id']}")
            st.write(f"Nombre: {video.get('nombre_video', 'Sin nombre')}")
            st.write("---")

# --- 3. Buscar por rango de fechas ---
elif opcion == "Buscar por rango de fechas":
    fecha_inicio = st.date_input("Fecha de inicio:")
    fecha_fin = st.date_input("Fecha de fin:")
    if st.button("Buscar"):
        resultados = collection.find({
            "fecha": {
                "$gte": pd.to_datetime(fecha_inicio),
                "$lte": pd.to_datetime(fecha_fin)
            }
        })
        for video in resultados:
            st.write(f"{video.get('nombre_video')} - {video.get('fecha')}")

# --- 4. Buscar palabra en subtítulos ---
elif opcion == "Buscar palabra en subtítulos":
    palabra = st.text_input("Palabra a buscar:")
    if palabra:
        resultados = collection.find({"subtitulos.texto": {"$regex": palabra, "$options": "i"}})
        for video in resultados:
            st.write(f"Video: {video.get('nombre_video')}")
            for sub in video.get("subtitulos", []):
                if palabra.lower() in sub.get("texto", "").lower():
                    st.write(f"  Tiempo: {sub.get('tiempo')} - Texto: {sub.get('texto')}")

# --- 5. Tabla de similitudes ---
elif opcion == "Similitud entre videos":
    video_id = st.text_input("Ingrese el ID del video:")
    if video_id:
        video = collection.find_one({"_id": video_id})
        if video and "similitudes" in video:
            df = pd.DataFrame(video["similitudes"])
            st.dataframe(df)
        else:
            st.warning("No se encontraron similitudes para este video.")

# --- 6. Red de similitudes ---
elif opcion == "Red de similitudes":
    video_id = st.text_input("ID del video origen:")
    umbral = st.slider("Umbral mínimo de similitud:", 0.0, 1.0, 0.5, 0.05)
    if video_id:
        video = collection.find_one({"_id": video_id})
        if video and "similitudes" in video:
            G = nx.Graph()
            G.add_node(video_id, label=video.get("nombre_video", "Origen"))

            for sim in video["similitudes"]:
                if sim["similitud"] >= umbral:
                    G.add_node(sim["video_id"], label=sim.get("nombre", ""))
                    G.add_edge(video_id, sim["video_id"], weight=sim["similitud"])

            pos = nx.spring_layout(G)
            plt.figure(figsize=(8, 6))
            nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue")
            labels = nx.get_edge_attributes(G, "weight")
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
            st.pyplot(plt)
        else:
            st.warning("No se encontraron datos de similitud para este video.")

