from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

    @property
    def label(self) -> str:
        return "Administrador" if self is UserRole.ADMIN else "Usuário"
