from pydantic import BaseModel, NonNegativeInt, computed_field


class ErrorResponse(BaseModel):
    """Forma única de todos los errores que regresa la API."""

    detail: str
    error_code: str | None = None


class PlayTime(BaseModel):
    """
    Tiempo de juego. Steam lo entrega en minutos; aquí se agregan
    las horas y un texto legible ("12 h 5 min").
    porque por default lo pone en minutos
    """

    minutes: NonNegativeInt

    @computed_field
    @property
    def hours(self) -> float:
        return round(self.minutes / 60, 1)

    @computed_field
    @property
    def formatted(self) -> str:
        hours, minutes = divmod(self.minutes, 60)
        if hours == 0:
            return f"{minutes} min"
        if minutes == 0:
            return f"{hours:,} h"
        return f"{hours:,} h {minutes} min"
