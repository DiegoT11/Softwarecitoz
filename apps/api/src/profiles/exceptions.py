from src.exceptions import ForbiddenError, NotFoundError


class ProfileNotFound(NotFoundError):
    error_code = "profile_not_found"

    def __init__(self, steam_id: str):
        self.steam_id = steam_id
        super().__init__(f"No existe un perfil de Steam con id={steam_id}")


class ProfilePrivate(ForbiddenError):
    error_code = "profile_private"

    def __init__(self, steam_id: str):
        self.steam_id = steam_id
        super().__init__(
            f"Los juegos del perfil id={steam_id} son privados"
        )
