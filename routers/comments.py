import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(tags=["comments"])

@router.post("/api/tasks/{task_id}/comments")
def add_comment(task_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    c = models.Comment(id=str(uuid.uuid4()), task_id=task_id, user_id=u.id, content=data["content"])
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "content": c.content, "created_at": c.created_at.isoformat() if c.created_at else None,
            "user": {"id": u.id, "name": u.name, "avatar_color": u.avatar_color}}

@router.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: str, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    c = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not c: raise HTTPException(404)
    if c.user_id != u.id and u.global_role != "ADMIN":
        raise HTTPException(403, "Não autorizado")
    db.delete(c); db.commit()
    return {"ok": True}
