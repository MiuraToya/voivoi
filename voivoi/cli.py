"""CLI エントリーポイント."""

from typing import Final

import typer

from voivoi.config.loader import save_config
from voivoi.config.paths import get_config_file
from voivoi.config.schema import Config

LOGO: Final[str] = """\
░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
 ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
 ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
  ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
  ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░ ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
   ░▒▓██▓▒░   ░▒▓██████▓▒░░▒▓█▓▒░  ░▒▓██▓▒░   ░▒▓██████▓▒░░▒▓█▓▒░
"""

app = typer.Typer()
config_app = typer.Typer()
app.add_typer(config_app, name="config")


def _print_config(config: Config) -> None:
    """Print config values in a user-friendly format."""
    typer.echo()
    typer.echo(typer.style("  LLM", bold=True))
    typer.echo(f"    model: {config.llm.model}")
    typer.echo()
    typer.echo(typer.style("  STT", bold=True))
    typer.echo(f"    language: {config.stt.language}")
    typer.echo()
    typer.echo(typer.style("  TTS", bold=True))
    typer.echo(f"    enabled: {str(config.tts.enabled).lower()}")


@config_app.command("init")
def config_init() -> None:
    """Initialize config file with default values."""
    config_file = get_config_file()

    if config_file.exists():
        typer.echo(
            typer.style(
                f"Config file already exists: {config_file}", fg=typer.colors.YELLOW
            )
        )
        return

    config = Config()
    save_config(config, config_file)
    typer.echo(
        typer.style(f"Created config file: {config_file}", fg=typer.colors.GREEN)
    )
    _print_config(config)


def run():
    print(LOGO)
