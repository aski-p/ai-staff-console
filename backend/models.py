"""SQLAlchemy ORM 모델 정의"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime
)
from database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    description = Column(Text, default="")
    system_prompt = Column(Text, default="")
    model_name = Column(String(100), default="qwen3-coder")
    telegram_name = Column(String(100), nullable=True, default=None)  # Telegram에서 호출용 별명 (예: 김팀장)
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deleted_at = Column(DateTime, nullable=True, default=None)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, unique=True, nullable=False)
    can_read_files = Column(Boolean, default=False)
    can_write_files = Column(Boolean, default=False)
    can_execute_shell = Column(Boolean, default=False)
    can_use_internet = Column(Boolean, default=False)
    can_access_medical_rag = Column(Boolean, default=False)
    can_access_insurance_rag = Column(Boolean, default=False)
    can_access_dailywon_rag = Column(Boolean, default=False)
    can_access_code_rag = Column(Boolean, default=False)


class RagCollection(Base):
    __tablename__ = "rag_collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    collection_path = Column(String(500), default="")
    agent_ids = Column(Text, default="[]")  # JSON array of agent IDs
    document_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Task(Base):
    __tablename__ = "tasks"

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_WAITING_APPROVAL = "waiting_approval"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    prompt = Column(Text, nullable=False)
    rag_collections = Column(Text, default="[]")  # JSON array
    status = Column(String(30), default=STATUS_PENDING)
    result = Column(Text, default="")
    error_message = Column(Text, default="")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=True)
    agent_id = Column(Integer, nullable=True)
    agent_name = Column(String(100), default="")
    action = Column(String(50), nullable=False)  # created, started, completed, approved, rejected, failed
    details = Column(Text, default="")
    permissions_used = Column(Text, default="{}")  # JSON object
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
