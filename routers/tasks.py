import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

def full_task(t):
    return {
        "id": t.id, "title": t.title, "description": t.description, "priority": t.priority,
        "position": t.position, "due_date": t.due_date.isoformat() if t.due_date else None,
        "column_id": t.column_id, "board_id": t.board_id, "created_by": t.created_by,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        "assignees": [{"user_id": a.user_id, "name": a.user.name if a.user else "", "avatar_color": a.user.avatar_color if a.user else "#6366f1"} for a in t.assignees],
        "labels": [{"label_id": tl.label_id, "name": tl.label.name if tl.label else "", "color": tl.label.color if tl.label else "#6366f1"} for tl in t.labels],
        "comments": [{"id": c.id, "content": c.content, "created_at": c.created_at.isoformat() if c.created_at else None,
                      "user": {"id": c.user.id, "name": c.user.name, "avatar_color": c.user.avatar_color} if c.user else None} for c in t.comments],
    }

@router.post("")
def create_task(data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    pos = db.query(models.Task).filter(models.Task.column_id == data["column_id"]).count()
    t = models.Task(id=str(uuid.uuid4()), board_id=data["board_id"], column_id=data["column_id"],
                    title=data["title"], priority=data.get("priority","MEDIUM"),
                    position=pos, created_by=u.id)
    db.add(t); db.commit(); db.refresh(t)
    return full_task(t)

@router.get("/{task_id}")
def get_task(task_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not t: raise HTTPException(404)
    return full_task(t)

@router.patch("/{task_id}")
def update_task(task_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not t: raise HTTPException(404)
    for field in ("title","description","priority","column_id","position"):
        if field in data: setattr(t, field, data[field])
    if "due_date" in data:
        from datetime import date
        t.due_date = date.fromisoformat(data["due_date"]) if data["due_date"] else None
    t.updated_at = datetime.utcnow()
    db.commit(); db.refresh(t)
    return full_task(t)

@router.delete("/{task_id}")
def delete_task(task_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not t: raise HTTPException(404)
    db.delete(t); db.commit()
    return {"ok": True}

@router.post("/{task_id}/assignees")
def add_assignee(task_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    if not db.query(models.TaskAssignee).filter_by(task_id=task_id, user_id=data["user_id"]).first():
        db.add(models.TaskAssignee(task_id=task_id, user_id=data["user_id"]))
        db.commit()
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    return full_task(t)

@router.delete("/{task_id}/assignees/{user_id}")
def remove_assignee(task_id: str, user_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    a = db.query(models.TaskAssignee).filter_by(task_id=task_id, user_id=user_id).first()
    if a: db.delete(a); db.commit()
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    return full_task(t)

@router.post("/{task_id}/labels")
def add_label(task_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    if not db.query(models.TaskLabel).filter_by(task_id=task_id, label_id=data["label_id"]).first():
        db.add(models.TaskLabel(task_id=task_id, label_id=data["label_id"]))
        db.commit()
    return full_task(db.query(models.Task).filter(models.Task.id == task_id).first())

@router.delete("/{task_id}/labels/{label_id}")
def remove_label(task_id: str, label_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    tl = db.query(models.TaskLabel).filter_by(task_id=task_id, label_id=label_id).first()
    if tl: db.delete(tl); db.commit()
    return full_task(db.query(models.Task).filter(models.Task.id == task_id).first())
