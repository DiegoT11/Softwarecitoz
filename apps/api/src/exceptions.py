class DomainError(Exception):
    """Base de las excepciones de dominio de la API."""

    error_code: str = "domain_error"


class NotFoundError(DomainError):
    error_code: str = "not_found"


class ForbiddenError(DomainError):
    error_code: str = "forbidden"


class ExternalServiceError(DomainError):
    """Un servicio externo (Steam) falló o no respondió."""

    error_code: str = "external_service_error"


class RateLimitedError(DomainError):
    """El servicio externo nos está limitando (HTTP 429)."""

    error_code: str = "rate_limited"
