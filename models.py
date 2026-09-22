import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, Text, Integer, Numeric, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"
    id              = Column(Text, primary_key=True, default=gen_uuid)
    name            = Column(Text, nullable=False)
    slug            = Column(Text, unique=True, nullable=False)
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)
    users           = relationship("User",  back_populates="organization")
    spaces          = relationship("Space", back_populates="organization")
    labels          = relationship("Label", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id              = Column(Text, primary_key=True, default=gen_uuid)
    organization_id = Column(Text, ForeignKey("organizations.id"))
    name            = Column(Text, nullable=False)
    email           = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    global_role     = Column(Text, nullable=False, default="MEMBER")
    avatar_color    = Column(Text, default="#6366f1")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)
    organization    = relationship("Organization", back_populates="users")
    space_memberships = relationship("SpaceMember", back_populates="user")
    assigned_tasks  = relationship("TaskAssignee", back_populates="user")
    comments        = relationship("Comment", back_populates="user")

class Space(Base):
    __tablename__ = "spaces"
    id              = Column(Text, primary_key=True, default=gen_uuid)
    organization_id = Column(Text, ForeignKey("organizations.id"))
    name            = Column(Text, nullable=False)
    description     = Column(Text)
    icon            = Column(Text, default="📋")
    created_by      = Column(Text, ForeignKey("users.id"))
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)
    organization    = relationship("Organization", back_populates="spaces")
    members         = relationship("SpaceMember", back_populates="space", cascade="all, delete-orphan")
    boards          = relationship("Board",       back_populates="space", cascade="all, delete-orphan")

class SpaceMember(Base):
    __tablename__ = "space_members"
    space_id = Column(Text, ForeignKey("spaces.id", ondelete="CASCADE"), primary_key=True)
    user_id  = Column(Text, ForeignKey("users.id",  ondelete="CASCADE"), primary_key=True)
    role     = Column(Text, default="MEMBER")
    space    = relationship("Space", back_populates="members")
    user     = relationship("User",  back_populates="space_memberships")

class Board(Base):
    __tablename__ = "boards"
    id          = Column(Text, primary_key=True, default=gen_uuid)
    space_id    = Column(Text, ForeignKey("spaces.id", ondelete="CASCADE"))
    name        = Column(Text, nullable=False)
    description = Column(Text)
    created_by  = Column(Text, ForeignKey("users.id"))
    created_at  = Column(DateTime(timezone=True), default=datetime.utcnow)
    space       = relationship("Space", back_populates="boards")
    columns     = relationship("KanbanColumn", back_populates="board", cascade="all, delete-orphan", order_by="KanbanColumn.position")
    tasks       = relationship("Task", back_populates="board", cascade="all, delete-orphan")

class KanbanColumn(Base):
    __tablename__ = "columns"
    id           = Column(Text, primary_key=True, default=gen_uuid)
    board_id     = Column(Text, ForeignKey("boards.id", ondelete="CASCADE"))
    name         = Column(Text, nullable=False)
    color        = Column(Text, default="#64748b")
    position     = Column(Integer, nullable=False, default=0)
    is_done_state = Column(Boolean, default=False)
    board        = relationship("Board", back_populates="columns")
    tasks        = relationship("Task",  back_populates="column", order_by="Task.position")

class Task(Base):
    __tablename__ = "tasks"
    id              = Column(Text, primary_key=True, default=gen_uuid)
    board_id        = Column(Text, ForeignKey("boards.id", ondelete="CASCADE"))
    column_id       = Column(Text, ForeignKey("columns.id"))
    title           = Column(Text, nullable=False)
    description     = Column(Text)
    priority        = Column(Text, default="MEDIUM")
    position        = Column(Integer, nullable=False, default=0)
    due_date        = Column(Date)
    created_by      = Column(Text, ForeignKey("users.id"))
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at      = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    board           = relationship("Board",        back_populates="tasks")
    column          = relationship("KanbanColumn", back_populates="tasks")
    assignees       = relationship("TaskAssignee", back_populates="task", cascade="all, delete-orphan")
    labels          = relationship("TaskLabel",    back_populates="task", cascade="all, delete-orphan")
    comments        = relationship("Comment",      back_populates="task", cascade="all, delete-orphan", order_by="Comment.created_at")

class Label(Base):
    __tablename__ = "labels"
    id              = Column(Text, primary_key=True, default=gen_uuid)
    organization_id = Column(Text, ForeignKey("organizations.id"))
    name            = Column(Text, nullable=False)
    color           = Column(Text, nullable=False, default="#6366f1")
    organization    = relationship("Organization", back_populates="labels")
    task_labels     = relationship("TaskLabel", back_populates="label", cascade="all, delete-orphan")

class TaskLabel(Base):
    __tablename__ = "task_labels"
    task_id  = Column(Text, ForeignKey("tasks.id",  ondelete="CASCADE"), primary_key=True)
    label_id = Column(Text, ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True)
    task     = relationship("Task",  back_populates="labels")
    label    = relationship("Label", back_populates="task_labels")

class TaskAssignee(Base):
    __tablename__ = "task_assignees"
    task_id = Column(Text, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Text, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    task    = relationship("Task", back_populates="assignees")
    user    = relationship("User", back_populates="assigned_tasks")

class Comment(Base):
    __tablename__ = "comments"
    id         = Column(Text, primary_key=True, default=gen_uuid)
    task_id    = Column(Text, ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id    = Column(Text, ForeignKey("users.id"))
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    task       = relationship("Task", back_populates="comments")
    user       = relationship("User", back_populates="comments")
