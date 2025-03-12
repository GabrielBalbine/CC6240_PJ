from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class User(UserCreate):
    id: int

    class Config:
        orm_mode = True

class CharacterCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)
    classe: str = Field(..., min_length=1, max_length=50)

class Character(CharacterCreate):
    id: int
    usuario_id: int

    class Config:
        orm_mode = True
