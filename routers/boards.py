import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(tags=["boards"])

def assignee_dict(a):
    return {"user_id": a.user_id, "name": a.user.name if a.user else "", "avatar_color": a.user.avatar_color if a.user else "#6366f1"}

def label_dict(tl):
    return {"label_id": tl.label_id, "name": tl.label.name if tl.label else "", "color": tl.label.color if tl.label else "#6366f1"}

def task_dict(t):
    return {"id": t.id, "title": t.title, "description": t.description, "priority": t.priority,
            "position": t.position, "due_date": t.due_date.isoformat() if t.due_date else None,
            "column_id": t.column_id, "board_id": t.board_id, "created_by": t.created_by,
            "assignees": [assignee_dict(a) for a in t.assignees],
            "labels": [label_dict(l) for l in t.labels]}

def col_dict(c):
    return {"id": c.id, "name": c.name, "color": c.color,
            "position": c.position, "is_done_state": c.is_done_state, "board_id": c.board_id}

@router.get("/api/spaces/{space_id}/boards")
def list_boards(space_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    boards = db.query(models.Board).filter(models.Board.space_id == space_id).all()
    return [{"id": b.id, "name": b.name, "description": b.description, "space_id": b.space_id} for b in boards]

@router.post("/api/spaces/{space_id}/boards")
def create_board(space_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    u = get_current_user(request, db)
    if u.global_role not in ("ADMIN", "MANAGER"):
        raise HTTPException(403, "Apenas ADMIN ou MANAGER")
    b = models.Board(id=str(uuid.uuid4()), space_id=space_id, name=data["name"],
                     description=data.get("description"), created_by=u.id)
    db.add(b)
    # Default columns
    for i, (name, color, done) in enumerate([("Backlog","#64748b",False),("Em andamento","#3b82f6",False),("Em revisão","#f59e0b",False),("Concluído","#22c55e",True)]):
        db.add(models.KanbanColumn(id=str(uuid.uuid4()), board_id=b.id, name=name, color=color, position=i, is_done_state=done))
    db.commit(); db.refresh(b)
    return {"id": b.id, "name": b.name, "description": b.description, "space_id": b.space_id}

@router.get("/api/boards/{board_id}")
def get_board(board_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    b = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not b: raise HTTPException(404, "Board not found")
    cols = db.query(models.KanbanColumn).filter(models.KanbanColumn.board_id == board_id).order_by(models.KanbanColumn.position).all()
    tasks = db.query(models.Task).filter(models.Task.board_id == board_id).order_by(models.Task.position).all()
    return {"id": b.id, "name": b.name, "description": b.description, "space_id": b.space_id,
            "columns": [col_dict(c) for c in cols], "tasks": [task_dict(t) for t in tasks]}
