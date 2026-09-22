import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/columns", tags=["columns"])

@router.post("/api/boards/{board_id}/columns")
def create_column(board_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    max_pos = db.query(models.KanbanColumn).filter(models.KanbanColumn.board_id == board_id).count()
    c = models.KanbanColumn(id=str(uuid.uuid4()), board_id=board_id, name=data["name"],
                            color=data.get("color","#64748b"), position=max_pos)
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "name": c.name, "color": c.color, "position": c.position, "board_id": c.board_id}

@router.patch("/{col_id}")
def update_column(col_id: str, data: dict, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    c = db.query(models.KanbanColumn).filter(models.KanbanColumn.id == col_id).first()
    if not c: raise HTTPException(404, "Column not found")
    if "name" in data: c.name = data["name"]
    if "color" in data: c.color = data["color"]
    db.commit(); db.refresh(c)
    return {"id": c.id, "name": c.name, "color": c.color, "position": c.position, "board_id": c.board_id}

@router.delete("/{col_id}")
def delete_column(col_id: str, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    c = db.query(models.KanbanColumn).filter(models.KanbanColumn.id == col_id).first()
    if not c: raise HTTPException(404)
    db.delete(c); db.commit()
    return {"ok": True}
