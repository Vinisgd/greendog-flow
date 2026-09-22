import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/spaces", tags=["spaces"])

def space_dict(s):
    return {"id": s.id, "name": s.name, "description": s.description,
            "icon": s.icon, "created_by": s.created_by,
            "organization_id": s.organization_id,
            "created_at": s.created_at.isoformat() if s.created_at else None}

@router.get("")
def list_spaces(request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    # ADMINs see all spaces; everyone else only sees spaces they're members of
    if u.global_role == "ADMIN":
        spaces = db.query(models.Space).filter(
            models.Space.organization_id == u.organization_id
        ).all()
    else:
        mids = [m.space_id for m in db.query(models.SpaceMember)
                .filter(models.SpaceMember.user_id == u.id).all()]
        spaces = db.query(models.Space).filter(models.Space.id.in_(mids)).all()
    return [space_dict(s) for s in spaces]

@router.post("")
def create_space(data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    if u.global_role != "ADMIN":
        raise HTTPException(403, "Apenas Administradores podem criar espaços")
    s = models.Space(
        id=str(uuid.uuid4()),
        organization_id=u.organization_id,
        name=data["name"],
        description=data.get("description"),
        icon=data.get("icon", "🏪"),
        created_by=u.id
    )
    db.add(s)
    db.flush()
    # Always add the creator as ADMIN
    db.add(models.SpaceMember(space_id=s.id, user_id=u.id, role="ADMIN"))
    # Add selected members
    for uid in data.get("member_ids", []):
        if uid != u.id:
            db.add(models.SpaceMember(space_id=s.id, user_id=uid, role="MEMBER"))
    db.commit()
    db.refresh(s)
    return space_dict(s)

@router.get("/{space_id}/members")
def get_members(space_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    members = db.query(models.SpaceMember).filter(
        models.SpaceMember.space_id == space_id
    ).all()
    return [{"space_id": m.space_id, "user_id": m.user_id, "role": m.role,
             "user": {"id": m.user.id, "name": m.user.name, "email": m.user.email,
                      "avatar_color": m.user.avatar_color}} for m in members]

@router.post("/{space_id}/members")
def add_member(space_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    if u.global_role != "ADMIN":
        raise HTTPException(403, "Apenas Administradores")
    existing = db.query(models.SpaceMember).filter_by(
        space_id=space_id, user_id=data["user_id"]
    ).first()
    if existing:
        raise HTTPException(409, "Usuário já é membro deste espaço")
    sm = models.SpaceMember(space_id=space_id, user_id=data["user_id"],
                            role=data.get("role", "MEMBER"))
    db.add(sm)
    db.commit()
    return {"space_id": space_id, "user_id": data["user_id"], "role": sm.role}

@router.delete("/{space_id}/members/{user_id}")
def remove_member(space_id: str, user_id: str, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    if u.global_role != "ADMIN":
        raise HTTPException(403, "Apenas Administradores")
    m = db.query(models.SpaceMember).filter_by(space_id=space_id, user_id=user_id).first()
    if m:
        db.delete(m)
        db.commit()
    return {"ok": True}
