# AI 직원 관리 콘솔 (AI Staff Console)

PGX 환경에서 여러 AI 직원(에이전트)을 생성·관리하고 작업을 지시할 수 있는 관리자 웹 콘솔입니다.

## 기술 스택

- **Frontend**: Next.js 15 + React 19 + TypeScript
- **Backend**: FastAPI + Python 3.12
- **Database**: SQLite (Docker volume에 저장)
- **LLM**: Ollama API (데afault: qwen3-coder)
- **Container**: Docker Compose

## 프로젝트 구조

```
ai-staff-console/
├── docker-compose.yml
├── README.md
├── frontend/              # Next.js 프론트엔드
│   ├── app/               # 페이지 컴포넌트들
│   │   ├── page.tsx       # 대시보드
│   │   ├── agents/        # AI 직원 목록 및 상세
│   │   ├── rag/           # RAG 컬렉션 관리
│   │   ├── tasks/         # 작업 지시
│   │   └── logs/          # 작업 로그
│   ├── lib/               # API 클라이언트, 타입 정의
│   └── Dockerfile
└── backend/               # FastAPI 백엔드
    ├── main.py            # API 서버 (모든 엔드포인트)
    ├── database.py        # SQLite 초기화
    ├── models.py          # SQLAlchemy 모델
    ├── schemas.py         # Pydantic 스키마
    ├── agents.py          # 시드 데이터 (기본 직원 5명)
    ├── permissions.py     # 권한 유틸리티
    ├── ollama_client.py   # Ollama API 클라이언트
    └── Dockerfile
```

## 설치 및 실행

### 필수 조건

- Docker + Docker Compose
- Ollama (로컬 설치 후 qwen3-coder 모델 다운로드)

### 실행

```bash
docker compose up -d --build
```

실행 후:

| 서비스 | URL | 비고 |
|--------|-----|------|
| Frontend | http://localhost:3000 | 관리자 콘솔 UI |
| Backend API | http://localhost:8000/docs | Swagger 문서 |

### 초기 데이터

시작 시 자동으로 생성됩니다:

- **기본 AI 직원 5명**: 개발자, 문서비서, 병원/논문 분석가, 보험/행정 담당자, DailyWon 기획자
- **RAG 컬렉션 7개**: baby_medical, ppp2r5d_papers, insurance, home_loan, dailywon_docs, code_projects, all_personal_docs

## Ollama 설정

### 모델 다운로드

```bash
ollama pull qwen3-coder
```

### 다른 모델로 변경

1. [Frontend]: AI 직원을 선택 → 상세 페이지에서 모델명 변경
2. [Backend]: `backend/agents.py` 시드 데이터의 `model_name` 수정

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/dashboard` | 대시보드 요약 |
| GET | `/agents` | 직원 목록 |
| POST | `/agents` | 직원 생성 |
| PUT/DELETE | `/agents/{id}` | 수정/삭제 |
| GET/PUT | `/permissions/{id}` | 권한 조회/수정 |
| GET | `/rag-collections` | RAG 컬렉션 목록 |
| POST | `/rag-collections` | RAG 컬렉션 생성 |
| GET | `/tasks` | 작업 목록 (status 필터링 가능) |
| POST | `/tasks` | 작업 생성 |
| POST | `/tasks/{id}/run` | 작업 실행 |
| POST | `/tasks/{id}/approve` | 승인 |
| POST | `/tasks/{id}/reject` | 반려 |
| GET | `/logs` | 작업 로그 |

## 보안 기본 원칙

- 위험 권한 (`can_write_files`, `can_execute_shell`, `can_use_internet`)은 기본적으로 **false**
- 첫 버전에서는 Ollama 호출까지만 실제 동작, 쉘 실행 기능은 구현 안 됨
- 삭제는 soft delete 방식 (실제 데이터 유지)

## 향후 추가 예정

- [ ] 로그인/인증 시스템
- [ ] 실제 파일 업로드 및 문서 처리
- [ ] Qdrant 임베딩 연동
- [ ] Git 작업 실행 파이프라인
- [ ] 승인 후 쉘 명령 실행 (안전하게)
