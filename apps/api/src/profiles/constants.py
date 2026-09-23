from enum import StrEnum


class PersonaStatus(StrEnum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    AWAY = "away"
    SNOOZE = "snooze"
    LOOKING_TO_TRADE = "looking_to_trade"
    LOOKING_TO_PLAY = "looking_to_play"


# `personastate` de Steam es un entero 0-6.
PERSONA_STATES = {
    0: PersonaStatus.OFFLINE,
    1: PersonaStatus.ONLINE,
    2: PersonaStatus.BUSY,
    3: PersonaStatus.AWAY,
    4: PersonaStatus.SNOOZE,
    5: PersonaStatus.LOOKING_TO_TRADE,
    6: PersonaStatus.LOOKING_TO_PLAY,
}


class Visibility(StrEnum):
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"
    PUBLIC = "public"


# `communityvisibilitystate` de Steam: 1 privado, 2 amigos, 3 público.
VISIBILITIES = {
    1: Visibility.PRIVATE,
    2: Visibility.FRIENDS_ONLY,
    3: Visibility.PUBLIC,
}


class GameSort(StrEnum):
    PLAYTIME = "playtime"
    RECENT = "recent"
    NAME = "name"
