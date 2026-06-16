"""AI 직원 관리 콘솔 - FastAPI 메인 서버"""

from datetime import datetime, timezone
import json as _json
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import init_db, get_db, engine
from models import Agent, Permission, RagCollection, Task, Log, Base
import ollama_client as ollama
from agents import seed_db
import schemas
import telegram_bot

# ── 앱 초기화 ──────────────────────────────────────
Base.metadata.create_all(bind=engine)
seed_db(next(get_db()))  # 소모기 세션으로 시드 완료 후 닫힘

app = FastAPI(
    title="AI Staff Console",
    description="PGX AI 직원 관리 대시보드 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health 체크 ───────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-staff-console"}


# ── Settings: Telegram ────────────────────────────────
class TelegramConfigRequest(BaseModel):
    bot_token: str
    active: bool = True

@app.get("/settings/telegram")
def get_telegram_settings():
    return telegram_bot.get_config()

@app.post("/settings/telegram")
async def set_telegram_settings(req: dict):
    """Bot Token 설정 + 활성/비활성 토글"""
    try:
        await telegram_bot.configure(
            bot_token=req.get("bot_token", ""),
            active=req.get("active", False),
        )
    except Exception as e:
        raise HTTPException(400, f"Telegram 설정 오류: {e}")
    return {"message": "Telegram 설정이 적용되었습니다.", "config": telegram_bot.get_config()}

@app.post("/settings/telegram/stop")
async def stop_telegram():
    """Telegram Polling 중지"""
    await telegram_bot.stop_polling()
    return {"message": "Telegram polling이 중지되었습니다."}


# ── 대시보드 요약 ──────────────────────────────────
@app.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    total = db.query(Agent).filter_by(deleted_at=None).count()
    active = db.query(Agent).filter_by(deleted_at=None, is_active=True).count()
    rag_count = db.query(RagCollection).count()
    pending = db.query(Task).filter_by(status=Task.STATUS_PENDING).count()
    return schemas.DashboardStats(
        total_agents=total,
        active_agents=active,
        rag_collections=rag_count,
        pending_tasks=pending,
    )


# ── Agent CRUD ─────────────────────────────────────
@app.get("/agents", response_model=list[schemas.AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).filter_by(deleted_at=None).order_by(Agent.id.desc()).all()


@app.post("/agents", response_model=schemas.AgentResponse)
def create_agent(agent_in: schemas.AgentCreate, db: Session = Depends(get_db)):
    a = Agent(**agent_in.model_dump())
    db.add(a)
    # 기본 권한 (모두 false)
    p = Permission(agent_id=a.id)
    db.add(p)
    db.commit()
    db.refresh(a)
    return a


@app.get("/agents/{agent_id}", response_model=schemas.AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.deleted_at.is_(None)).first()
    if not a:
        raise HTTPException(404, "Agent not found")
    return a


@app.put("/agents/{agent_id}", response_model=schemas.AgentResponse)
def update_agent(agent_id: int, body: schemas.AgentUpdate, db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.deleted_at.is_(None)).first()
    if not a:
        raise HTTPException(404, "Agent not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.deleted_at.is_(None)).first()
    if not a:
        raise HTTPException(404, "Agent not found")
    # Soft delete
    a.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": f"Agent {agent_id} soft-deleted"}


# ── Permissions ───────────────────────────────────
@app.get("/permissions/{agent_id}", response_model=schemas.PermissionResponse)
def get_permissions(agent_id: int, db: Session = Depends(get_db)):
    p = db.query(Permission).filter_by(agent_id=agent_id).first()
    if not p:
        raise HTTPException(404, "Permissions not found for this agent")
    return p


@app.put("/permissions/{agent_id}", response_model=schemas.PermissionResponse)
def update_permissions(
    agent_id: int, body: schemas.PermissionUpdate, db: Session = Depends(get_db)
):
    p = db.query(Permission).filter_by(agent_id=agent_id).first()
    if not p:
        raise HTTPException(404, "Permissions not found for this agent")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


# ── RAG Collections ───────────────────────────────
@app.get("/rag-collections", response_model=list[schemas.RagResponse])
def list_rags(db: Session = Depends(get_db)):
    return db.query(RagCollection).order_by(RagCollection.id.desc()).all()


@app.post("/rag-collections", response_model=schemas.RagResponse)
def create_rag(rag_in: schemas.RagCreate, db: Session = Depends(get_db)):
    r = RagCollection(**rag_in.model_dump())
    # agent_ids를 JSON 문자열로 저장
    if hasattr(r, "agent_ids") and isinstance(r.agent_ids, list):
        r.agent_ids = _json.dumps(r.agent_ids)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


# ── Tasks ──────────────────────────────────────────
@app.get("/tasks", response_model=list[schemas.TaskResponse])
def list_tasks(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Task)
    if status:
        q = q.filter_by(status=status)
    return q.order_by(Task.id.desc()).all()


@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == task_in.agent_id, Agent.deleted_at.is_(None)).first()
    if not a:
        raise HTTPException(404, "Agent not found")
    t = Task(
        agent_id=task_in.agent_id,
        title=task_in.title,
        prompt=task_in.prompt,
        rag_collections=_json.dumps(task_in.rag_collections or []),
        status=Task.STATUS_PENDING,
    )
    db.add(t)
    _log(db, task_id=t.id, agent_id=a.id, agent_name=a.name, action="created", details=f"작업 생성: {task_in.title}")
    db.commit()
    db.refresh(t)
    return t


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter_by(id=task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    return t


@app.post("/tasks/{task_id}/run", response_model=schemas.TaskResponse)
def run_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter_by(id=task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    if t.status != Task.STATUS_PENDING:
        raise HTTPException(400, f"작업은 pending 상태에서만 실행 가능합니다 (현재: {t.status})")

    agent = db.query(Agent).filter(Agent.id == t.agent_id, Agent.deleted_at.is_(None)).first()
    if not agent:
        raise HTTPException(404, "Agent not found")

    # Ollama 호출
    try:
        result = ollama.generate_response(
            model_name=agent.model_name,
            system_prompt=agent.system_prompt,
            user_prompt=t.prompt,
        )
    except Exception as e:
        result = f"[실행 오류] {e}"

    t.result = result
    now = datetime.now(timezone.utc)
    t.completed_at = now

    # requires_approval 체크
    if agent.requires_approval:
        t.status = Task.STATUS_WAITING_APPROVAL
        _log(db, task_id=t.id, agent_id=agent.id, agent_name=agent.name, action="waiting_approval", details=f"결과 생성됨 (승인 대기): {t.title}")
    else:
        t.status = Task.STATUS_COMPLETED
        _log(db, task_id=t.id, agent_id=agent.id, agent_name=agent.name, action="completed", details=f"작업 완료: {t.title}")

    db.commit()
    db.refresh(t)
    return t


@app.post("/tasks/{task_id}/approve", response_model=schemas.TaskResponse)
def approve_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter_by(id=task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    if t.status != Task.STATUS_WAITING_APPROVAL:
        raise HTTPException(400, f"이 작업은 승인 대기 상태가 아닙니다 (현재: {t.status})")

    agent = db.query(Agent).filter_by(id=t.agent_id).first()
    t.status = Task.STATUS_COMPLETED
    t.completed_at = datetime.now(timezone.utc)
    _log(db, task_id=t.id, agent_id=t.agent_id, agent_name=agent.name if agent else "", action="approved", details=f"작업 승인: {t.title}")
    db.commit()
    db.refresh(t)
    return t


@app.post("/tasks/{task_id}/reject", response_model=schemas.TaskResponse)
def reject_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter_by(id=task_id).first()
    if not t:
        raise HTTPException(404, "Task not found")
    if t.status != Task.STATUS_WAITING_APPROVAL:
        raise HTTPException(400, f"이 작업은 승인 대기 상태가 아닙니다 (현재: {t.status})")

    agent = db.query(Agent).filter_by(id=t.agent_id).first()
    t.status = Task.STATUS_FAILED
    t.completed_at = datetime.now(timezone.utc)
    _log(db, task_id=t.id, agent_id=t.agent_id, agent_name=agent.name if agent else "", action="rejected", details=f"작업 반려: {t.title}")
    db.commit()
    db.refresh(t)
    return t


# ── Logs ───────────────────────────────────────────
@app.get("/logs")
def list_logs(db: Session = Depends(get_db)):
    return db.query(Log).order_by(Log.id.desc()).limit(200).all()


# ── Internal helpers ───────────────────────────────
def _log(db: Session, *, agent_id: Optional[int], task_id: Optional[int],
         agent_name: str, action: str, details: str, permissions_used: dict = None):
    log = Log(
        task_id=task_id,
        agent_id=agent_id,
        agent_name=agent_name,
        action=action,
        details=details,
        permissions_used=_json.dumps(permissions_used or {}),
    )
    db.add(log)
