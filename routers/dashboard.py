from datetime import date
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    assignee_rows = db.query(models.TaskAssignee).filter(models.TaskAssignee.user_id == u.id).all()
    task_ids = [a.task_id for a in assignee_rows]
    tasks = db.query(models.Task).filter(models.Task.id.in_(task_ids)).all() if task_ids else []
    today = date.today()
    overdue = sum(1 for t in tasks if t.due_date and t.due_date < today)
    by_priority = {}
    for t in tasks:
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
    def mini(t):
        return {"id": t.id, "title": t.title, "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "column_id": t.column_id, "board_id": t.board_id,
                "labels": [{"label_id": tl.label_id, "name": tl.label.name if tl.label else "",
                             "color": tl.label.color if tl.label else "#6366f1"} for tl in t.labels]}
    return {"my_tasks": [mini(t) for t in tasks], "overdue_count": overdue, "by_priority": by_priority}
