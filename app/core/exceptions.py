from ninja.errors import HttpError

class NotFoundError(HttpError):
    def __init__(self, message="Resource not found"):
        super().__init__(404, message)


class BadRequestError(HttpError):
    def __init__(self, message="Bad request"):
        super().__init__(400, message)


class UnauthorizedError(HttpError):
    def __init__(self, message="Unauthorized"):
        super().__init__(401, message)


class ForbiddenError(HttpError):
    def __init__(self, message="Forbidden"):
        super().__init__(403, message)