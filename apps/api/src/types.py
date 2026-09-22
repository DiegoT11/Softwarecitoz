from datetime import datetime
from typing import Annotated

from fastapi import Path
from pydantic import BeforeValidator

# SteamID64: 17 dígitos que siempre empiezan con 7656119.
STEAM_ID_PATTERN = r"^7656119\d{10}$"

SteamIdPath = Annotated[
    str,
    Path(
        pattern=STEAM_ID_PATTERN,
        description="SteamID64 del usuario (17 dígitos)",
        examples=["76561197960435530"],
    ),
]


def _zero_to_none(value: object) -> object:
    """Steam usa 0 para indicar "sin fecha"; lo convertimos a None."""
    if value in (0, "0"):
        return None
    return value


# Pydantic convierte automáticamente un int unix (segundos) a datetime
# en UTC; aquí solo cubrimos el caso especial del 0.
# es para mejor formato
UnixTimestamp = Annotated[datetime | None, BeforeValidator(_zero_to_none)]
