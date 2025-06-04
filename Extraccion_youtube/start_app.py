# start_app.py (ubicado dentro de Extraccion_youtube)
import os
import sys
import subprocess

# Ruta absoluta al directorio raíz (Extraccion_youtube)
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)  # 👈 clave para que 'etl' sea visible

# Ejecuta el script Streamlit con ruta relativa
subprocess.run(["streamlit", "run", os.path.join("etl", "app.py")], cwd=project_root)
