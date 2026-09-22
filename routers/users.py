import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
import models
from auth import get_current_user, get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])

def user_dict(u):
    return {"id": u.id, "name": u.name, "email": u.email, "global_role": u.global_role,
            "avatar_color": u.avatar_color, "is_active": u.is_active,
            "organization_id": u.organization_id,
            "created_at": u.created_at.isoformat() if u.created_at else None}

@router.get("")
def list_users(request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    users = db.query(models.User).filter(models.User.organization_id == u.organization_id).all()
    return [user_dict(x) for x in users]

@router.patch("/{user_id}")
def update_user(user_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    cu = get_current_user(request, db)
    if cu.global_role != "ADMIN": raise HTTPException(403, "Apenas ADMIN")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(404)
    if "name" in data: user.name = data["name"]
    if "global_role" in data: user.global_role = data["global_role"]
    if "is_active" in data: user.is_active = data["is_active"]
    db.commit(); db.refresh(user)
    return user_dict(user)

@router.post("/invite")
def invite_user(data: dict, request: Request, db: Session = Depends(get_db)):
    cu = get_current_user(request, db)
    if cu.global_role != "ADMIN": raise HTTPException(403, "Apenas ADMIN")
    if db.query(models.User).filter(models.User.email == data["email"]).first():
        raise HTTPException(409, "Email já cadastrado")
    new_user = models.User(
        id=str(uuid.uuid4()), organization_id=cu.organization_id,
        name=data["name"], email=data["email"],
        hashed_password=get_password_hash(data["password"]),
        global_role=data.get("global_role","MEMBER"),
        avatar_color=data.get("avatar_color","#6366f1"), is_active=True)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return user_dict(new_user)
