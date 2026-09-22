import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from database import engine
        import models
        models.Base.metadata.create_all(bind=engine)
        print("Tables created/verified.")
    except Exception as e:
        print(f"DB init failed (will retry on requests): {e}")
    try:
        from seed import seed
        seed()
    except Exception as e:
        print(f"Seed skipped: {e}")
    yield

app = FastAPI(title="KanbanFlow", lifespan=lifespan)

from routers import auth, users, spaces, boards, columns, tasks, comments, labels, dashboard

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(spaces.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(labels.router)
app.include_router(dashboard.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

static_dir = os.path.join(os.path.dirname(__file__), "static")
assets_dir = os.path.join(static_dir, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/api/debug/token")
async def debug_token(request: Request):
    import jwt as pyjwt, os
    SECRET_KEY = os.environ.get("SECRET_KEY", "kanbanflow-secret-key-2024-change-in-prod")
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"error": "No Bearer token"}
    token = auth_header[7:].strip()
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"ok": True, "sub": payload.get("sub"), "exp": str(payload.get("exp"))}
    except Exception as e:
        return {"ok": False, "error": str(e), "type": type(e).__name__}

@app.get("/{full_path:path}")
def spa(full_path: str):
    index = os.path.join(static_dir, "index.html")
    return FileResponse(index)

