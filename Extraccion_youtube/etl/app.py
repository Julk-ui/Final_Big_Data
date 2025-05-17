import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Configuración
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Youtube_database"
COLLECTION_NAME = "subtitulos"

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

st.set_page_config(page_title="Subtítulos YouTube", layout="wide")
st.title("🔍 Aplicación de consulta de subtítulos YouTube")

# --- Función auxiliar para formatear subtítulos ---
def mostrar_subtitulos(subtitulos):
    df = pd.DataFrame(subtitulos)
    df["start"] = df["start"].apply(lambda s: f"{s:.2f} s")
    return df[["start", "text"]]

# 1. Consultar por ID del video
st.header("1. Buscar por ID del video")
video_id = st.text_input("Ingresa el ID del video:")

if video_id:
    video = collection.find_one({"video_id": video_id})
    if video:
        st.success(f"Título: {video['titulo']}")
        st.write("🕒 Fecha de descarga:", video["fecha_descarga"])
        st.write("🔗 URL:", video["url"])
        st.dataframe(mostrar_subtitulos(video["texto"]), use_container_width=True)
    else:
        st.warning("❌ No se encontró un video con ese ID.")

# 2. Buscar por texto en el título (requiere índice de texto en MongoDB)
st.header("2. Buscar por texto en el título")
texto_busqueda = st.text_input("Ingresa una palabra clave para buscar en el título:")

if texto_busqueda:
    resultados = collection.find({"$text": {"$search": texto_busqueda}})
    for video in resultados:
        st.markdown(f"- 📹 **{video['titulo']}** - [Ver video]({video['url']})")

# 3. Buscar por rango de fechas de descarga
st.header("3. Buscar por rango de fechas")
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Desde", datetime(2024, 1, 1))
with col2:
    fecha_fin = st.date_input("Hasta", datetime.today())

if fecha_inicio and fecha_fin:
    resultados = collection.find({
        "fecha_descarga": {
            "$gte": fecha_inicio.strftime("%Y-%m-%d"),
            "$lte": fecha_fin.strftime("%Y-%m-%d")
        }
    })
    st.write("📅 Videos encontrados:")
    for video in resultados:
        st.markdown(f"- 📹 **{video['titulo']}** ({video['fecha_descarga']})")

# 4. Buscar palabra específica en subtítulos
st.header("4. Buscar palabra en subtítulos")
palabra_clave = st.text_input("Escribe una palabra para buscar en los subtítulos:")

if palabra_clave:
    resultados = collection.find({
        "texto.text": {"$regex": palabra_clave, "$options": "i"}
    })

    count = 0
    for video in resultados:
        coincidencias = [sub for sub in video["texto"] if palabra_clave.lower() in sub["text"].lower()]
        if coincidencias:
            st.markdown(f"### 📽️ {video['titulo']} ({video['video_id']})")
            st.markdown(f"[Ver video]({video['url']})")
            df = pd.DataFrame(coincidencias)
            df["start"] = df["start"].apply(lambda s: f"{s:.2f} s")
            st.dataframe(df[["start", "text"]])
            count += 1
    if count == 0:
        st.warning("No se encontraron coincidencias.")

# 5. Ver similitudes de un video específico
st.header("5. Consultar similitudes de un video")
video_sim = st.text_input("ID del video para ver sus similitudes:")

if video_sim:
    doc = collection.find_one({"video_id": video_sim})
    if doc and "similitudes" in doc:
        df = pd.DataFrame(doc["similitudes"])
        df = df.sort_values(by="similitud", ascending=False)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No se encontraron similitudes para ese video.")

# 6. Buscar red de videos similares por umbral
st.header("6. Red de relaciones por similitud")
col1, col2 = st.columns([3, 1])
with col1:
    video_red = st.text_input("ID del video base:")
with col2:
    umbral = st.slider("Umbral de similitud", min_value=0.0, max_value=1.0, value=0.8)

if video_red:
    doc = collection.find_one({"video_id": video_red})
    if doc and "similitudes" in doc:
        relaciones = [
            (video_red, sim["video_id"], sim["similitud"])
            for sim in doc["similitudes"]
            if sim["similitud"] >= umbral
        ]

        G = nx.Graph()
        G.add_node(video_red, label=doc["titulo"])
        for origen, destino, peso in relaciones:
            G.add_edge(origen, destino, weight=peso)

        st.subheader("🔗 Red de videos relacionados")
        pos = nx.spring_layout(G, seed=42)
        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color="gray", node_size=1000, font_size=10)
        st.pyplot(fig)
    else:
        st.warning("No se encontraron relaciones o similitudes para ese video.")

#Con la conexion exitosa
