# src.exceptions.py

class AppEEARSError(Exception):
    """Base exception class for AppEEARS API errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class LoginError(AppEEARSError):
    """Exception raised when login fails."""
    pass

class RequestError(AppEEARSError):
    """Exception raised for errors during API requests."""
    pass
