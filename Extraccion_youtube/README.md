# 🎥 Proyecto de Extracción y Consulta de Subtítulos de YouTube

Este proyecto permite extraer automáticamente subtítulos desde un canal de YouTube, almacenarlos en MongoDB y Neo4j, y consultar la información desde una aplicación web con Streamlit.

---

## 🚀 Requisitos

Instala las dependencias necesarias:

```bash
python -m pip install -r requirements.txt
Si requirements.txt no está disponible, puedes instalar manualmente con:

pip install typer==0.3.2
pip install colorama==0.4.4
pip install shellingham==1.4.0
pip install pytest==6.2.4
pip install SpeechRecognition==3.14.2
pip install pyttsx3==2.90
pip install pymongo==4.6.1
pip install youtube-transcript-api==1.0.3
pip install streamlit
pip install neo4j
⚙️ Inicializar la Aplicación
Verifica la conexión a MongoDB:

python -m Extraccion_youtube.etl.cli init

Extrae y carga los videos desde YouTube:

python -m Extraccion_youtube.etl.cli extraer-y-cargar
🔗 Ingresa una URL como:
https://www.youtube.com/@Cconstitucional

(Opcional) Limpia la base de datos:

python -m Extraccion_youtube.etl.cli limpiar-bd

💻 Ejecutar la aplicación web

Ejecuta la app con Streamlit:

'''streamlit run etl/app.py
'''
O, si usas el lanzador auxiliar:

python start_app.py
🔎 Funcionalidades de la App Web
Buscar por ID del video.

Buscar por palabra clave en el título.

Filtrar por rango de fechas de descarga.

Buscar una palabra dentro de los subtítulos.

Consultar similitudes desde Neo4j (tabla).

Visualizar grafo de similitudes por umbral desde Neo4j.

(Opcional) Visualizar grafo desde archivo .json cargado manualmente.

🧠 Tecnologías utilizadas
Python 3.11

MongoDB Atlas

Neo4j Aura (cloud)

Streamlit

YouTube Transcript API

Typer (CLI)

NetworkX + Matplotlib (visualización de grafos)

📂 Estructura del proyecto

Extraccion_youtube/
│
├── etl/
│   ├── app.py              # Aplicación web (Streamlit)
│   ├── cli.py              # Interfaz de línea de comandos
│   ├── config.py           # Configuración de credenciales
│   ├── controller.py       # Lógica de inserción Mongo/Neo4j
│   ├── database.py         # Conexión a Mongo y Neo4j
│   ├── extract.py          # Extracción de videos y subtítulos
│   ├── crearGrafo.py       # Carga de similitudes en Neo4j desde archivo JSON
│   └── ...
│
├── start_app.py            # Script para lanzar Streamlit
├── requirements.txt        # Dependencias
├── README.md               # Instrucciones del proyecto

✨ Autores:
Gerson Julian Rincon Peña
Manuel Salazar
Este proyecto fue desarrollado para el Taller de Big Data de la Maestría en Analítica de Datos.
