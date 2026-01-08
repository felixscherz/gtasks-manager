class DomainError(Exception):
    """Base class for domain exceptions."""

    pass


class APIError(DomainError):
    """Raised when an API call fails."""

    pass


class AuthenticationError(DomainError):
    """Raised when authentication fails or is missing."""

    pass


class NotFoundError(DomainError):
    """Raised when a resource is not found."""

    pass


class ValidationError(DomainError):
    """Raised when validation fails."""

    pass


class RateLimitError(DomainError):
    """Raised when API rate limit is exceeded."""

    pass


class NetworkError(DomainError):
    """Raised when a network error occurs."""

    pass
