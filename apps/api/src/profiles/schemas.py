from datetime import UTC, datetime

from pydantic import BaseModel, computed_field

from src.profiles.constants import PersonaStatus, Visibility
from src.schemas import PlayTime


class CurrentGame(BaseModel):
    app_id: int
    name: str


class ProfileOut(BaseModel):
    steam_id: str
    name: str
    real_name: str | None
    profile_url: str
    avatar_url: str
    status: PersonaStatus
    visibility: Visibility
    country_code: str | None
    created_at: datetime | None
    last_online_at: datetime | None
    currently_playing: CurrentGame | None

    @computed_field
    @property
    def account_age_years(self) -> int | None:
        if self.created_at is None:
            return None
        return (datetime.now(UTC) - self.created_at).days // 365


class PlatformPlayTime(BaseModel):
    windows: PlayTime
    mac: PlayTime
    linux: PlayTime
    steam_deck: PlayTime


class GameOut(BaseModel):
    app_id: int
    name: str
    icon_url: str | None
    playtime_total: PlayTime
    playtime_last_two_weeks: PlayTime
    playtime_by_platform: PlatformPlayTime
    last_played_at: datetime | None


class LibraryOut(BaseModel):
    steam_id: str
    game_count: int
    total_playtime: PlayTime
    games: list[GameOut]


class RecentActivityOut(BaseModel):
    steam_id: str
    game_count: int
    total_playtime_last_two_weeks: PlayTime
    games: list[GameOut]
