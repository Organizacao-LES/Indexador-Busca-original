# app/exceptions/user_exceptions.py

class UserException(Exception):
    """Base exception for user-related errors."""
    pass

class UserNotFoundException(UserException):
    """Raised when a user is not found."""
    def __init__(self, detail: str = "User not found."):
        self.detail = detail
        super().__init__(self.detail)

class UserConflictException(UserException):
    """Raised when a user creation or update conflicts with existing data (e.g., duplicate login/email)."""
    def __init__(self, detail: str = "User conflict."):
        self.detail = detail
        super().__init__(self.detail)

class UserPermissionException(UserException):
    """Raised when a user does not have the necessary permissions."""
    def __init__(self, detail: str = "Operation not permitted."):
        self.detail = detail
        super().__init__(self.detail)
