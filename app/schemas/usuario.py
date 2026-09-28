from pydantic import BaseModel, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(min_length=8)
    acepto_tratamiento: bool
    
    @field_validator("acepto_tratamiento")
    @classmethod
    def exigir_si(cls, v):
        if not v:
            raise ValueError("Sin consentimiento no hay cuenta")
        return v


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str