"""This module provides the RP To-Do CLI."""

from pathlib import Path
from typing import List, Optional


import typer

from etl import ERRORS, __app_name__, __version__, config, controller, database

app = typer.Typer()


@app.command()
def init() -> None:
    """Initialize the MongoDB database."""
    try:
        # Verificamos la conexión a MongoDB
        db_handler = database.DatabaseHandler()
        typer.secho("Connected to MongoDB successfully!", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Failed to connect to MongoDB: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(1)


def get_todoer():
    """Obtiene la conexión a MongoDB."""
    return database.DatabaseHandler()


@app.command()
def add(path: str) -> None:
    """Add a new audio file to the database."""
    db_handler = database.DatabaseHandler()
    # Simulando extracción de texto (esto deberías reemplazarlo con tu lógica real)
    text = "Texto extraído del audio"
    bigdata = "Datos adicionales"

    audio = db_handler.add_audio(path)

    typer.secho(f"Audio agregado: {audio}", fg=typer.colors.GREEN)


@app.command(name="list")
def list_all() -> None:
    """List all audio files from the database."""
    db_handler = database.DatabaseHandler()
    audio_list = db_handler.get_audios()

    if not audio_list:
        typer.secho("No hay audios en la base de datos.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.secho("\nLista de audios:\n", fg=typer.colors.BLUE, bold=True)

    # Obtener todas las claves (columnas) de los documentos
    all_keys = set()
    for audio in audio_list:
        all_keys.update(audio.keys())

    all_keys = sorted(all_keys)  # Ordenamos las claves

    # Imprimir encabezado
    headers = " | ".join(all_keys)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)

    # Imprimir cada documento
    for audio in audio_list:
        row = " | ".join(str(audio.get(key, "")) for key in all_keys)
        typer.secho(row, fg=typer.colors.BLUE)

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)


@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="¿Eliminar todos los audios?",
        help="Forzar eliminación sin confirmación.",
    ),
) -> None:
    """Elimina todos los documentos de la base de datos."""
    db_handler = database.DatabaseHandler()

    if force:
        deleted_count = db_handler.remove_all()
        typer.secho(f"Se eliminaron {deleted_count} audios.", fg=typer.colors.GREEN)
    else:
        typer.echo("Operación cancelada.")
