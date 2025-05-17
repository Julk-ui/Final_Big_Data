import pandas as pd
import json
import openpyxl

# Cargar el archivo JSONL
jsonl_path = "videos_extraidos.jsonl"
data = []

with open(jsonl_path, "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

# Crear DataFrame solo con columnas necesarias
df = pd.DataFrame(data)[["video_id", "titulo", "url", "longitud", "estado", "detalle_error"]]

# Exportar a Excel
output_path = "reporte_videos.xlsx"
df.to_excel(output_path, index=False)

print(f"Excel generado correctamente en: {output_path}")
