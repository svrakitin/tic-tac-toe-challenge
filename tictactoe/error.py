from falcon import HTTPInternalServerError


class GameError(HTTPInternalServerError):
    pass


class GameValueError(GameError, ValueError):
    pass
