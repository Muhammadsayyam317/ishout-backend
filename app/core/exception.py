from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        details: list | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "details": details,
            },
        )


class NotFoundException(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class InternalServerErrorException(AppException):
    def __init__(self, message="Internal server error"):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message)


class BadRequestException(AppException):
    def __init__(self, message="Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)


class UnauthorizedException(AppException):
    def __init__(self, message="Unauthorized"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)
