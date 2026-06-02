from fastapi import HTTPException, status


class UserException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(UserException):
    def __init__(self, detail: str = "User not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserConflictException(UserException):
    def __init__(self, detail: str = "User conflict."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
