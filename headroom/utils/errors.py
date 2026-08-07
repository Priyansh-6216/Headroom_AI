class HeadroomError(Exception):
    """Base exception class for Headroom."""
    pass

class CompressionError(HeadroomError):
    """Raised when compression fails."""
    pass

class ConfigurationError(HeadroomError):
    """Raised for invalid configuration."""
    pass
