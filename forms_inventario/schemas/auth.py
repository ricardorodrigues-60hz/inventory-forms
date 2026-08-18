from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    senha: str
