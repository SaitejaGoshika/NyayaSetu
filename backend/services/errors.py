class ModelUnavailableError(RuntimeError):
    """The trusted case prediction model has not been provisioned."""


class ExtractionError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
