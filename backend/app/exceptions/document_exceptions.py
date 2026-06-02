from fastapi import HTTPException, status


class DocumentException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class DocumentValidationException(DocumentException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class DocumentConflictException(DocumentException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DocumentNotFoundException(DocumentException):
    def __init__(self, detail: str = "Documento não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
