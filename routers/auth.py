from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import verify_password, create_access_token, get_current_user, COOKIE_NAME, TOKEN_EXPIRE_DAYS
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

def user_dict(u):
    return {
        "id": str(u.id),
        "name": u.name,
        "email": u.email,
        "global_role": u.global_role,
        "avatar_color": u.avatar_color,
        "organization_id": str(u.organization_id) if u.organization_id else None,
        "is_active": u.is_active,
    }

@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Conta desativada")

    token = create_access_token({"sub": str(user.id)})

    # Set HttpOnly cookie — works in all contexts including iframes
    # secure=True em produção (HTTPS); False apenas em localhost
    import os as _os
    is_prod = _os.environ.get("RAILWAY_ENVIRONMENT") or _os.environ.get("RENDER") or _os.environ.get("PRODUCTION")
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=bool(is_prod),
    )

    return {
        "access_token": token,   # also returned for clients that prefer headers
        "token_type": "bearer",
        "user": user_dict(user),
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME)
    return {"ok": True}

@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return user_dict(user)
