from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.user import (
    AuthResponse,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    UserOut,
)
from app.security import create_access_token
from app.services import user_service


router = APIRouter(
    prefix="/api/auth",
    tags=["User Account"]
)


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        token=create_access_token(user.id),
        user=UserOut(id=user.id, name=user.name, email=user.email)
    )


@router.post("/register", status_code=201, response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):

    try:
        user = user_service.register_user(
            db, request.name, request.email, request.password
        )
    except user_service.EmailAlreadyRegistered:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    client_ip = http_request.client.host if http_request.client else "unknown"

    try:
        user = user_service.authenticate(db, request.email, request.password, client_ip)
    except user_service.TooManyAttempts:
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts. Please try again in 15 minutes."
        )
    except user_service.InvalidCredentials:
        # Same message for "no such email" and "wrong password"
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return _auth_response(user)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return MeResponse(user=UserOut(id=user.id, name=user.name, email=user.email))
