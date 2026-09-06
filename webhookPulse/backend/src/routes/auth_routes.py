from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from src.controllers.auth_controller import (
    login,
    register,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register_endpoint(data: RegisterRequest):
    return register(
        email=data.email,
        password=data.password,
        company_name=data.company_name,
    )


@router.post("/login")
def login_endpoint(data: LoginRequest):
    return login(
        email=data.email,
        password=data.password,
    )