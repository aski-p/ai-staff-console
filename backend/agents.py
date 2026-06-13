""" 초기 AI 직원 및 RAG 컬렉션 자동 생성 """

import json as _json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import Agent, Permission, RagCollection


DEFAULT_AGENTS = [
    {
        "name": "개발자 에이전트",
        "role": "developer",
        "description": "코드 작성, 디버깅, 코드 리뷰를 담당하는 엔지니어 AI",
        "system_prompt": "너는 숙련된 소프트웨어 개발자다. 사용자의 요청에 따라 코드를 작성하고 디버깅 한다. 명확하고 효율적인 코드를 작성하라.",
        "model_name": "qwen3-coder",
        "is_active": True,
        "requires_approval": False,
    },
    {
        "name": "문서비서 에이전트",
        "role": "document_assistant",
        "description": "문서 요약, 번역, 텍스트 편집을 담당하는 비서 AI",
        "system_prompt": "너는 문서 작업에 특화된 비서다. 요약, 번역, 정리를 정확하고 간결하게 수행한다.",
        "model_name": "qwen3-coder",
        "is_active": True,
        "requires_approval": False,
    },
    {
        "name": "병원/논문 분석가",
        "role": "medical_analyst",
        "description": "의료 기록과 의학 논문을 분석하는 전문 AI",
        "system_prompt": "너는 의료 및 학술 논문 분석 전문가다. 임상 데이터와 연구 결과를 정확히 해석하고 요약한다.",
        "model_name": "qwen3-coder",
        "is_active": True,
        "requires_approval": True,
    },
    {
        "name": "보험/행정 담당자",
        "role": "insurance_admin",
        "description": "보험금 청구, 행정 절차, 규제 준수 분석을 담당하는 AI",
        "system_prompt": "너는 보험 및 administrative 분야의 전문가다. 규정 기반의 정확한 판단과 절차를 제시한다.",
        "model_name": "qwen3-coder",
        "is_active": True,
        "requires_approval": True,
    },
    {
        "name": "DailyWon 기획자",
        "role": "dailywon_planner",
        "description": "DailyWon 플랫폼의 콘텐츠 기획 및 운영 분석을 담당하는 AI",
        "system_prompt": "너는 DailyWon의 콘텐츠 기획자다. 데이터 기반의 전략과 아이디어를 제안한다.",
        "model_name": "qwen3-coder",
        "is_active": True,
        "requires_approval": False,
    },
]

# 역할 → 기본 권한 매핑
DEFAULT_PERMISSIONS = {
    "developer": {
        "can_read_files": True,
        "can_write_files": True,
        "can_execute_shell": False,
        "can_use_internet": True,
        "can_access_medical_rag": False,
        "can_access_insurance_rag": False,
        "can_access_dailywon_rag": False,
        "can_access_code_rag": True,
    },
    "document_assistant": {
        "can_read_files": True,
        "can_write_files": False,
        "can_execute_shell": False,
        "can_use_internet": True,
        "can_access_medical_rag": False,
        "can_access_insurance_rag": False,
        "can_access_dailywon_rag": False,
        "can_access_code_rag": False,
    },
    "medical_analyst": {
        "can_read_files": True,
        "can_write_files": False,
        "can_execute_shell": False,
        "can_use_internet": True,
        "can_access_medical_rag": True,
        "can_access_insurance_rag": False,
        "can_access_dailywon_rag": False,
        "can_access_code_rag": False,
    },
    "insurance_admin": {
        "can_read_files": True,
        "can_write_files": False,
        "can_execute_shell": False,
        "can_use_internet": True,
        "can_access_medical_rag": False,
        "can_access_insurance_rag": True,
        "can_access_dailywon_rag": False,
        "can_access_code_rag": False,
    },
    "dailywon_planner": {
        "can_read_files": True,
        "can_write_files": False,
        "can_execute_shell": False,
        "can_use_internet": True,
        "can_access_medical_rag": False,
        "can_access_insurance_rag": False,
        "can_access_dailywon_rag": True,
        "can_access_code_rag": False,
    },
}

DEFAULT_RAG_COLLECTIONS = [
    {"name": "baby_medical", "description": "신생아 및 소아 의료 데이터베이스", "collection_path": "/data/baby_medical", "agent_ids": ["medical_analyst"]},
    {"name": "ppp2r5d_papers", "description": "의학 논문 컬렉션 (PPP2R5D 데이터셋 관련)", "collection_path": "/data/ppp2r5d_papers", "agent_ids": ["medical_analyst"]},
    {"name": "insurance", "description": "보험 상품 및 청구 규정 문서", "collection_path": "/data/insurance", "agent_ids": ["insurance_admin"]},
    {"name": "home_loan", "description": "주택ローン 및 금융 규정 자료", "collection_path": "/data/home_loan", "agent_ids": ["insurance_admin"]},
    {"name": "dailywon_docs", "description": "DailyWon 플랫폼 운영 문서", "collection_path": "/data/dailywon", "agent_ids": ["dailywon_planner"]},
    {"name": "code_projects", "description": "프로젝트 소스코드 및 기술 문서", "collection_path": "/data/code", "agent_ids": ["developer"]},
    {"name": "all_personal_docs", "description": "개인 문서 전체 아카이브 (모든 직원 접근 가능)", "collection_path": "/data/personal", "agent_ids": []},
]


def seed_db(db: Session) -> None:
    """초기 데이터 생성 (이미 있으면 스킵)"""

    # ── 1. AI 직원 5명 생성 ──────────────────────
    existing_count = db.query(Agent).filter_by(deleted_at=None).count()
    if existing_count > 0:
        return  # 이미 시드됨

    for agent_data in DEFAULT_AGENTS:
        agent = Agent(**agent_data)
        db.add(agent)
        db.flush()

        # ── 2. 권한 등록 ────────────────────────
        role = agent_data["role"]
        perms = DEFAULT_PERMISSIONS.get(role, {})
        p = Permission(
            agent_id=agent.id,
            **{k: v for k, v in perms.items()},
        )
        db.add(p)

    db.flush()

    # 역할→ID 맵핑 (RAG 접근용)
    role_to_id = {}
    agents = db.query(Agent).filter_by(deleted_at=None).all()
    for a in agents:
        for d in DEFAULT_AGENTS:
            if d["role"] == a.role:
                role_to_id[d["role"]] = a.id
                break

    # ── 3. RAG 컬렉션 생성 ───────────────────────
    for rc_data in DEFAULT_RAG_COLLECTIONS:
        agent_ids_list = []
        for rname in rc_data.get("agent_ids", []):
            if rname in role_to_id:
                agent_ids_list.append(role_to_id[rname])

        # all_personal_docs는 모든 직원 접근 가능
        if rc_data["name"] == "all_personal_docs":
            agent_ids_list = [a.id for a in agents]

        rc = RagCollection(
            name=rc_data["name"],
            description=rc_data["description"],
            collection_path=rc_data["collection_path"],
            agent_ids=_json.dumps(agent_ids_list),
            document_count=0,
        )
        db.add(rc)

    db.commit()
    print(f"[seed_db] Created {len(DEFAULT_AGENTS)} agents + permissions + {len(DEFAULT_RAG_COLLECTIONS)} RAG collections")
