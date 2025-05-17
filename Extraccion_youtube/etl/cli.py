"""CLI para extracción y carga de videos con subtítulos a MongoDB."""

import typer
from Extraccion_youtube.etl.extract import extract_all_videos_batching
from Extraccion_youtube.etl.controller import VideoController
from Extraccion_youtube.etl.database import DatabaseHandler

app = typer.Typer()


@app.command()
def init() -> None:
    """Verifica conexión con MongoDB."""
    try:
        _ = DatabaseHandler()
        typer.secho("✅ Conexión a MongoDB exitosa.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ Falló la conexión: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def extraer_y_cargar(
    channel_url: str = typer.Option(None, "--channel-url", "-u", help="URL del canal de YouTube"),
    max_threads: int = 4,
    batch_size: int = 100
) -> None:
    """Extrae videos del canal y los carga a MongoDB."""
    if not channel_url:
        channel_url = typer.prompt("🔗 Por favor, ingresa la URL del canal de YouTube")

    print("🟢 Ejecutando función extraer_y_cargar()")
    typer.secho("⏳ Iniciando extracción...", fg=typer.colors.BLUE)

    resultados = extract_all_videos_batching(channel_url, max_threads=max_threads, batch_size=batch_size)

    typer.secho(f"🎬 {len(resultados)} videos extraídos. Cargando a MongoDB...", fg=typer.colors.BLUE)
    controller = VideoController()
    count = controller.insertar_videos(resultados)

    typer.secho(f"✅ {count} videos insertados correctamente.", fg=typer.colors.GREEN)


@app.command()
def limpiar_bd(force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Confirma la eliminación de todos los videos.")) -> None:
    """Elimina todos los videos en la base de datos."""
    if not force:
        typer.confirm("¿Estás seguro de que deseas eliminar todos los videos?", abort=True)

    db = DatabaseHandler()
    eliminados = db.remove_all()
    typer.secho(f"🗑️ {eliminados} documentos eliminados de MongoDB.", fg=typer.colors.RED)


if __name__ == "__main__":
    app()