import uuid
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization, User, Space, SpaceMember, Board, KanbanColumn, Task, TaskAssignee, Label, TaskLabel
from auth import get_password_hash

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Organization).filter_by(slug="acme-corp").first():
            print("Database already seeded, skipping.")
            return
        print("Seeding database...")
        
        now = datetime.utcnow()

        # Organization
        org_id = str(uuid.uuid4())
        db.execute(
            Organization.__table__.insert(),
            {"id": org_id, "name": "Acme Corp", "slug": "acme-corp", "created_at": now}
        )
        
        # Users
        hashed = get_password_hash("admin123")
        users_data = [
            ("admin@acme.com", "Admin User", "ADMIN", "#ef4444"),
            ("manager@acme.com", "Maria Manager", "MANAGER", "#f59e0b"),
            ("dev1@acme.com", "Dev One", "MEMBER", "#22c55e"),
            ("dev2@acme.com", "Dev Two", "MEMBER", "#3b82f6"),
            ("viewer@acme.com", "View User", "VIEWER", "#8b5cf6"),
        ]
        user_ids = []
        for email, name, role, color in users_data:
            uid = str(uuid.uuid4())
            db.execute(User.__table__.insert(), {
                "id": uid, "organization_id": org_id, "name": name, "email": email,
                "hashed_password": hashed, "global_role": role, "avatar_color": color,
                "is_active": True, "created_at": now
            })
            user_ids.append(uid)
        
        admin_id, manager_id, dev1_id, dev2_id, viewer_id = user_ids
        
        # Space
        space_id = str(uuid.uuid4())
        db.execute(Space.__table__.insert(), {
            "id": space_id, "organization_id": org_id, "name": "Desenvolvimento",
            "description": "Espaço principal de desenvolvimento", "icon": "💻",
            "created_by": admin_id, "created_at": now
        })
        
        # Space members
        for uid in user_ids:
            db.execute(SpaceMember.__table__.insert(), {"space_id": space_id, "user_id": uid, "role": "MEMBER"})
        
        # Board
        board_id = str(uuid.uuid4())
        db.execute(Board.__table__.insert(), {
            "id": board_id, "space_id": space_id, "name": "Sprint Q1",
            "description": "Sprint do primeiro trimestre", "created_by": admin_id, "created_at": now
        })
        
        # Columns
        cols_data = [
            ("Backlog", "#64748b", 0, False),
            ("Em andamento", "#3b82f6", 1, False),
            ("Em revisão", "#f59e0b", 2, False),
            ("Concluído", "#22c55e", 3, True),
        ]
        col_ids = []
        for name, color, pos, is_done in cols_data:
            cid = str(uuid.uuid4())
            db.execute(KanbanColumn.__table__.insert(), {
                "id": cid, "board_id": board_id, "name": name, "color": color,
                "position": pos, "is_done_state": is_done
            })
            col_ids.append(cid)
        
        backlog_id, in_progress_id, in_review_id, done_id = col_ids
        
        # Labels
        labels_data = [
            ("Bug", "#ef4444"),
            ("Feature", "#3b82f6"),
            ("Melhoria", "#22c55e"),
            ("Urgente", "#f97316"),
            ("Docs", "#8b5cf6"),
        ]
        label_ids = []
        for lname, lcolor in labels_data:
            lid = str(uuid.uuid4())
            db.execute(Label.__table__.insert(), {
                "id": lid, "organization_id": org_id, "name": lname, "color": lcolor
            })
            label_ids.append(lid)
        
        bug_id, feature_id, melhoria_id, urgente_id, docs_id = label_ids
        
        # Tasks
        today = date.today()
        tasks_data = [
            ("Setup inicial do projeto", "Configurar repositório e estrutura base", "HIGH", backlog_id, [admin_id], [feature_id], today + timedelta(days=7)),
            ("Implementar autenticação", "JWT login e refresh token", "CRITICAL", in_progress_id, [dev1_id], [feature_id, urgente_id], today + timedelta(days=2)),
            ("Criar endpoints da API", "CRUD completo para tarefas e usuários", "HIGH", in_progress_id, [dev1_id, dev2_id], [feature_id], today + timedelta(days=5)),
            ("Corrigir bug no login", "Usuário não consegue logar em alguns casos", "CRITICAL", in_review_id, [dev2_id], [bug_id, urgente_id], today - timedelta(days=1)),
            ("Documentação da API", "Swagger e README atualizado", "LOW", backlog_id, [viewer_id], [docs_id], today + timedelta(days=14)),
            ("Otimizar queries do banco", "Reduzir tempo de resposta das consultas", "MEDIUM", in_review_id, [dev1_id], [melhoria_id], today + timedelta(days=3)),
            ("Deploy em produção", "Configurar CI/CD e fazer deploy", "HIGH", done_id, [admin_id, manager_id], [feature_id], today - timedelta(days=2)),
            ("Testes automatizados", "Cobertura mínima de 80%", "MEDIUM", backlog_id, [dev2_id], [feature_id, melhoria_id], today + timedelta(days=10)),
        ]
        
        for i, (title, desc, priority, col_id, assignee_ids, task_label_ids, due) in enumerate(tasks_data):
            tid = str(uuid.uuid4())
            db.execute(Task.__table__.insert(), {
                "id": tid, "board_id": board_id, "column_id": col_id, "title": title,
                "description": desc, "priority": priority, "position": i, "due_date": due,
                "created_by": admin_id, "created_at": now, "updated_at": now
            })
            for uid in assignee_ids:
                db.execute(TaskAssignee.__table__.insert(), {"task_id": tid, "user_id": uid})
            for lid in task_label_ids:
                db.execute(TaskLabel.__table__.insert(), {"task_id": tid, "label_id": lid})
        
        db.commit()
        print("Seeding database... Done!")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()
