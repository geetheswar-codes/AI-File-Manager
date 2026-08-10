import re

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Enforce a strong password policy.
        """

        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long."
            )

        if not re.search(r"[A-Z]", password):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", password):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", password):
            raise ValueError(
                "Password must contain at least one number."
            )

        if not re.search(
            r"""[!@#$%^&*()_\-+=\[\]{}|\\:;\"'<>,.?/`~]""",
            password,
        ):
            raise ValueError(
                "Password must contain at least one special character."
            )

        if " " in password:
            raise ValueError(
                "Password cannot contain spaces."
            )

        return password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str