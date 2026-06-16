"""Pydantic 스키마 정의 (v2)"""

from datetime import datetime, timezone
from typing import Optional, Any
from pydantic import BaseModel


# ── Agent ──────────────────────────────────────────
class AgentCreate(BaseModel):
    name: str
    role: str
    description: str = ""
    system_prompt: str = ""
    model_name: str = "qwen3-coder"
    telegram_name: Optional[str] = None  # Telegram 호출용 별명 (ex: 김팀장)
    is_active: bool = True
    requires_approval: bool = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_name: Optional[str] = None
    telegram_name: Optional[str] = None
    is_active: Optional[bool] = None
    requires_approval: Optional[bool] = None

    class Config:
        extra = "ignore"


class AgentResponse(BaseModel):
    id: int
    name: str
    role: str
    description: str
    system_prompt: str
    model_name: str
    telegram_name: Optional[str] = None
    is_active: bool
    requires_approval: bool
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Permission ─────────────────────────────────────
class PermissionUpdate(BaseModel):
    can_read_files: Optional[bool] = None
    can_write_files: Optional[bool] = None
    can_execute_shell: Optional[bool] = None
    can_use_internet: Optional[bool] = None
    can_access_medical_rag: Optional[bool] = None
    can_access_insurance_rag: Optional[bool] = None
    can_access_dailywon_rag: Optional[bool] = None
    can_access_code_rag: Optional[bool] = None


class PermissionResponse(BaseModel):
    id: int
    agent_id: int
    can_read_files: bool
    can_write_files: bool
    can_execute_shell: bool
    can_use_internet: bool
    can_access_medical_rag: bool
    can_access_insurance_rag: bool
    can_access_dailywon_rag: bool
    can_access_code_rag: bool

    class Config:
        from_attributes = True


# ── RagCollection ──────────────────────────────────
class RagCreate(BaseModel):
    name: str
    description: str = ""
    collection_path: str = ""
    agent_ids: Optional[list[int]] = None
    document_count: int = 0


class RagResponse(BaseModel):
    id: int
    name: str
    description: str
    collection_path: str
    agent_ids: Any
    document_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Task ───────────────────────────────────────────
class TaskCreate(BaseModel):
    agent_id: int
    title: str
    prompt: str
    rag_collections: Optional[list[str]] = None


class TaskResponse(BaseModel):
    id: int
    agent_id: int
    title: str
    prompt: str
    rag_collections: Any
    status: str
    result: str
    error_message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Log ────────────────────────────────────────────
class LogResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    agent_id: Optional[int] = None
    agent_name: str
    action: str
    details: str
    permissions_used: Any
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ───────────────────────────────────────
class DashboardStats(BaseModel):
    total_agents: int
    active_agents: int
    rag_collections: int
    pending_tasks: int
