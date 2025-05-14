from typing import Optional

class AppError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str, details: Optional[str] = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self):
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }
