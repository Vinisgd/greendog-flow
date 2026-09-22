import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/labels", tags=["labels"])

@router.get("")
def list_labels(request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    labels = db.query(models.Label).filter(models.Label.organization_id == u.organization_id).all()
    return [{"id": l.id, "name": l.name, "color": l.color} for l in labels]

@router.post("")
def create_label(data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    l = models.Label(id=str(uuid.uuid4()), organization_id=u.organization_id, name=data["name"], color=data.get("color","#6366f1"))
    db.add(l); db.commit(); db.refresh(l)
    return {"id": l.id, "name": l.name, "color": l.color}

@router.delete("/{label_id}")
def delete_label(label_id: str, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    if u.global_role not in ("ADMIN","MANAGER"): raise HTTPException(403)
    l = db.query(models.Label).filter(models.Label.id == label_id).first()
    if not l: raise HTTPException(404)
    db.delete(l); db.commit()
    return {"ok": True}

@router.patch("/{label_id}")
def update_label(label_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    if u.global_role not in ("ADMIN","MANAGER"):
        raise HTTPException(403, "Apenas ADMIN ou MANAGER")
    l = db.query(models.Label).filter(models.Label.id == label_id).first()
    if not l: raise HTTPException(404)
    if "name" in data: l.name = data["name"]
    if "color" in data: l.color = data["color"]
    db.commit(); db.refresh(l)
    return {"id": l.id, "name": l.name, "color": l.color}
