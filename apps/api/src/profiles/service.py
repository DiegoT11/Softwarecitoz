from datetime import UTC, datetime

from src.profiles import schemas
from src.profiles.constants import (
    PERSONA_STATES,
    VISIBILITIES,
    GameSort,
    PersonaStatus,
    Visibility,
)
from src.profiles.exceptions import ProfileNotFound, ProfilePrivate
from src.schemas import PlayTime
from src.steam.client import ICON_URL, SteamClient
from src.steam.schemas import GameRaw, PlayerSummaryRaw

_NEVER = datetime.min.replace(tzinfo=UTC)


def _to_profile(raw: PlayerSummaryRaw) -> schemas.ProfileOut:
    currently_playing = None
    if raw.gameid is not None:
        currently_playing = schemas.CurrentGame(
            app_id=int(raw.gameid),
            name=raw.gameextrainfo or "",
        )
    return schemas.ProfileOut(
        steam_id=raw.steamid,
        name=raw.personaname,
        real_name=raw.realname,
        profile_url=raw.profileurl,
        avatar_url=raw.avatarfull,
        status=PERSONA_STATES.get(raw.personastate, PersonaStatus.OFFLINE),
        visibility=VISIBILITIES.get(
            raw.communityvisibilitystate, Visibility.PRIVATE),
        country_code=raw.loccountrycode,
        created_at=raw.timecreated,
        last_online_at=raw.lastlogoff,
        currently_playing=currently_playing,
    )


def _to_game(raw: GameRaw) -> schemas.GameOut:
    icon_url = None
    if raw.img_icon_url:
        icon_url = ICON_URL.format(
            appid=raw.appid, icon_hash=raw.img_icon_url)
    return schemas.GameOut(
        app_id=raw.appid,
        name=raw.name,
        icon_url=icon_url,
        playtime_total=PlayTime(minutes=raw.playtime_forever),
        playtime_last_two_weeks=PlayTime(minutes=raw.playtime_2weeks),
        playtime_by_platform=schemas.PlatformPlayTime(
            windows=PlayTime(minutes=raw.playtime_windows_forever),
            mac=PlayTime(minutes=raw.playtime_mac_forever),
            linux=PlayTime(minutes=raw.playtime_linux_forever),
            steam_deck=PlayTime(minutes=raw.playtime_deck_forever),
        ),
        last_played_at=raw.rtime_last_played,
    )


def _sort_games(
        games: list[schemas.GameOut],
        sort: GameSort) -> list[schemas.GameOut]:
    match sort:
        case GameSort.PLAYTIME:
            return sorted(
                games,
                key=lambda g: g.playtime_total.minutes,
                reverse=True,
            )
        case GameSort.RECENT:
            return sorted(
                games,
                key=lambda g: g.last_played_at or _NEVER,
                reverse=True,
            )
        case GameSort.NAME:
            return sorted(games, key=lambda g: g.name.casefold())


async def get_profile(
        steam: SteamClient, steam_id: str) -> schemas.ProfileOut:
    """
    Obtiene el perfil básico de un usuario de Steam.

    Args:
        steam (SteamClient): cliente de la Steam Web API.
        steam_id (str): SteamID64 del usuario.

    Returns:
        ProfileOut: perfil con fechas y estado ya convertidos.
    """
    raw = await steam.get_player_summary(steam_id)
    if raw is None:
        raise ProfileNotFound(steam_id)
    return _to_profile(raw)


async def get_library(
        steam: SteamClient,
        steam_id: str,
        sort: GameSort,
        limit: int | None) -> schemas.LibraryOut:
    """
    Obtiene la biblioteca de juegos de un usuario.

    Args:
        steam (SteamClient): cliente de la Steam Web API.
        steam_id (str): SteamID64 del usuario.
        sort (GameSort): criterio de orden de los juegos.
        limit (int | None): máximo de juegos a regresar.

    Returns:
        LibraryOut: juegos con tiempos convertidos y total acumulado.
    """
    raw = await steam.get_owned_games(steam_id)
    if raw.games is None:
        raise ProfilePrivate(steam_id)

    games = _sort_games([_to_game(g) for g in raw.games], sort)
    total = sum(g.playtime_forever for g in raw.games)
    return schemas.LibraryOut(
        steam_id=steam_id,
        game_count=raw.game_count or len(raw.games),
        total_playtime=PlayTime(minutes=total),
        games=games[:limit],
    )


async def get_recent_activity(
        steam: SteamClient, steam_id: str) -> schemas.RecentActivityOut:
    """
    Obtiene los juegos jugados en las últimas dos semanas.

    Args:
        steam (SteamClient): cliente de la Steam Web API.
        steam_id (str): SteamID64 del usuario.

    Returns:
        RecentActivityOut: juegos recientes ordenados por tiempo
        jugado en las últimas dos semanas.
    """
    raw = await steam.get_recently_played_games(steam_id)
    if raw.total_count is None:
        raise ProfilePrivate(steam_id)

    games = sorted(
        (_to_game(g) for g in raw.games),
        key=lambda g: g.playtime_last_two_weeks.minutes,
        reverse=True,
    )
    total = sum(g.playtime_2weeks for g in raw.games)
    return schemas.RecentActivityOut(
        steam_id=steam_id,
        game_count=raw.total_count,
        total_playtime_last_two_weeks=PlayTime(minutes=total),
        games=games,
    )
