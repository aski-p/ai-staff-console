"""Ollama 로컬 LLM 클라이언트"""

from datetime import timedelta
import httpx


OLLAMA_BASE = "http://host.docker.internal:11434"


def generate_response(model_name: str, system_prompt: str, user_prompt: str) -> str:
    """Ollama chat API 호출"""
    url = f"{OLLAMA_BASE}/api/chat"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt or "너는 유능한 AI 어시스턴트다."},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    try:
        with httpx.Client(timeout=timedelta(minutes=5)) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "(빈 응답)")
    except httpx.ConnectError:
        return "[오류] Ollama 서버에 연결할 수 없습니다. (host.docker.internal:11434)"
    except Exception as e:
        return f"[오류] {e}"


def list_models() -> list[dict]:
    """사용 가능한 모델 목록 조회"""
    url = f"{OLLAMA_BASE}/api/tags"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return [{"name": m["name"]} for m in data.get("models", [])]
    except Exception as e:
        print(f"Model list error: {e}")
        return []
