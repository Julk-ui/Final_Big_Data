import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase, basic_auth
from utils import set_background  # Esta función ya está bien definida en utils.py

# ✅ Esta debe ser la primera llamada de Streamlit
st.set_page_config(page_title="Relatoría Aplicación de consulta", layout="wide")

# ✅ Aplica el fondo
set_background("fondo.png")

# Neo4j
NEO4J_URI = "neo4j+s://75905f35.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "gXRnVMtlUXW-L1BjZz6R0QDE3XyRul7tvtttVooG3tU"
NEO4J_DB = "neo4j"

# Configuración MongoDB
MONGO_URI = "mongodb+srv://Julk89:RkiDLsRMprjpxM2i@cluster0.g4h8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Youtube_database"
COLLECTION_NAME = "subtitulos"

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

st.markdown("""
    <div style='background-color: rgba(255, 255, 255, 0.85); padding: 20px; border-radius: 10px;'>
""", unsafe_allow_html=True)

st.title("🔍 Relatoría Aplicación de consulta del Canal De La Corte Costitucional")

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

# 2. Buscar por texto en el título
st.header("2. Buscar por palabra en título o subtítulos")
texto_busqueda = st.text_input("Ingresa una palabra para buscar en título o subtítulos:")

if texto_busqueda:
    resultados = list(collection.find({"$text": {"$search": texto_busqueda}}))
    if resultados:
        for video in resultados:
            nombre = video.get('titulo', 'Sin título')
            url = video.get('url', '#')
            st.markdown(f"- 📹 **{nombre}** - [Ver video]({url})")
    else:
        st.warning("❌ No se encontraron resultados para esa búsqueda.")

# 3. Buscar por rango de fechas de descarga
st.header("3. Buscar por rango de fechas")
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Desde", datetime(2024, 1, 1))
with col2:
    fecha_fin = st.date_input("Hasta", datetime(2024, 1, 2))

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

# 5. Consultar similitudes desde Neo4j
st.header("5. Consultar similitudes desde Neo4j")
video_sim_neo = st.text_input("🔎 Ingresa el ID del video:")

if video_sim_neo:
    def obtener_similitudes(video_id):
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
            with driver.session(database=NEO4J_DB) as session:
                result = session.run("""
                    MATCH (v:Video {video_id: $video_id})-[r:SIMILAR_A]->(otro:Video)
                    RETURN otro.video_id AS relacionado, r.similitud AS similitud
                    ORDER BY r.similitud DESC
                """, video_id=video_id)
                data = result.data()
            driver.close()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"❌ Error al consultar Neo4j: {e}")
            return pd.DataFrame()

    df_sim = obtener_similitudes(video_sim_neo)
    if not df_sim.empty:
        st.dataframe(df_sim)
    else:
        st.warning("⚠️ No se encontraron similitudes para ese video.")

# 6. Visualizar red de videos similares desde Neo4j
st.header("6. Visualizar red de videos similares desde Neo4j")
video_grafo = st.text_input("🎥 ID del video base para grafo:")
umbral_neo = st.slider("🎯 Umbral de similitud", min_value=0.0, max_value=1.0, value=0.8)

if video_grafo:
    def construir_grafo_similitud(video_id, umbral):
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
            with driver.session(database=NEO4J_DB) as session:
                result = session.run("""
                    MATCH (v:Video {video_id: $video_id})-[r:SIMILAR_A]->(otro:Video)
                    WHERE r.similitud >= $umbral
                    RETURN v.video_id AS origen, otro.video_id AS destino, r.similitud AS peso
                """, video_id=video_id, umbral=int(umbral))
                relaciones = result.data()
            driver.close()
            G = nx.Graph()
            for rel in relaciones:
                G.add_edge(rel["origen"], rel["destino"], weight=rel["peso"])
            return G
        except Exception as e:
            st.error(f"❌ Error al construir grafo: {e}")
            return nx.Graph()

    umbral_entero = int(umbral_neo * 100)
    st.write(f"🎯 Umbral aplicado: {umbral_entero}")
    grafo = construir_grafo_similitud(video_grafo, umbral_entero)

    if grafo.number_of_edges() > 0:
        pos = nx.spring_layout(grafo, seed=42)
        fig, ax = plt.subplots(figsize=(10, 8))
        weights = [grafo[u][v]['weight'] for u, v in grafo.edges()]
        nx.draw(grafo, pos, with_labels=True, node_color='lightblue', edge_color=weights,
                edge_cmap=plt.cm.Blues, node_size=1000, font_size=10, width=2)
        st.pyplot(fig)
    else:
        st.warning("❌ No hay relaciones por encima del umbral.")

# Cierre del contenedor visual
st.markdown("""
    <div style='background-color: rgba(255, 255, 255, 0.85); padding: 25px; border-radius: 15px;'>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)