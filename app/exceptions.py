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

class UserNameTooShortError(AppError):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="USR_01",
            message="Nome deve ter pelo menos 3 caracteres.",
            details="Name must be at least 3 characters long"
        )

class EmailAlreadyExistsError(AppError):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="USR_02",
            message="E-mail já cadastrado.",
            details="A user with this email already exists"
        )

class WeakPasswordError(AppError):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="USR_03",
            message="Credenciais inválidas. Por favor, reveja.",
            details="Password must be at least 6 characters long and contain at least one letter and one number"
        )
