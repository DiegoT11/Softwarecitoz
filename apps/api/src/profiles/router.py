from typing import Annotated

from fastapi import APIRouter, Query

from src.profiles import schemas, service
from src.profiles.constants import GameSort
from src.schemas import ErrorResponse
from src.steam.dependencies import SteamClientDep
from src.types import SteamIdPath

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
    responses={
        404: {"model": ErrorResponse, "description": "Perfil no existe"},
        502: {"model": ErrorResponse, "description": "Steam falló"},
    },
)


@router.get("/{steam_id}", response_model=schemas.ProfileOut)
async def read_profile(steam_id: SteamIdPath, steam: SteamClientDep):
    return await service.get_profile(steam, steam_id)


@router.get(
    "/{steam_id}/games",
    response_model=schemas.LibraryOut,
    responses={403: {"model": ErrorResponse}},
)
async def read_library(
        steam_id: SteamIdPath,
        steam: SteamClientDep,
        sort: GameSort = GameSort.PLAYTIME,
        limit: Annotated[int | None, Query(ge=1, le=1000)] = None):
    return await service.get_library(steam, steam_id, sort, limit)


@router.get(
    "/{steam_id}/recent-games",
    response_model=schemas.RecentActivityOut,
    responses={403: {"model": ErrorResponse}},
)
async def read_recent_activity(
        steam_id: SteamIdPath, steam: SteamClientDep):
    return await service.get_recent_activity(steam, steam_id)
