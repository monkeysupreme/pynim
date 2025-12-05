# pynim/net/logger.py
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "debug": "dim white",
    "success": "bold green"
})

console = Console(theme=theme)

def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console)]
    )

    logging.getLogger("rich").setLevel(logging.ERROR)
