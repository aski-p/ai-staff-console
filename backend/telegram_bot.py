"""Telegram Bot 모듈 — aiogram 3.x 기반 polling + 메시지 핸들러"""

import os, json, asyncio
from datetime import datetime, timezone
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy.orm import Session

from database import get_db
from models import Agent
import ollama_client as ollama

# ── State ────────────────────────────────────────
_bot: Optional[Bot] = None
_token: Optional[str] = None
_is_polling: bool = False
_task: Optional[asyncio.Task] = None


_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "telegram_config.json")


def _load_config() -> dict:
    if os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH) as f:
            return json.load(f)
    return {}


def _save_config(cfg: dict):
    with open(_CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get_config() -> dict:
    cfg = _load_config()
    return {
        "bot_token": cfg.get("bot_token", "")[:10] + "..." if cfg.get("bot_token") else "",
        "is_active": cfg.get("active", False),
        "polling": _is_polling,
    }


async def configure(bot_token: str, active: bool):
    """Bot 토큰 설정 + 활성/비활성 토글"""
    global _bot, _token, _is_polling, _task

    cfg = _load_config()
    cfg["bot_token"] = bot_token
    cfg["active"] = active
    _save_config(cfg)

    if active and bot_token:
        _token = bot_token
        _bot = Bot(token=_token)
        await start_polling()
    else:
        await stop_polling()


async def start_polling():
    global _is_polling, _task
    if _is_polling or not _bot:
        return
    dp = Dispatcher()
    dp.message.register(handle_message)
    _task = asyncio.create_task(_bot.feed_webhook_updates(dp))  # polling fallback
    asyncio.create_task(
        _start_poll_worker(dp)
    )
    _is_polling = True


async def _start_poll_worker(dp: Dispatcher):
    try:
        await dp.start_polling(_bot, allowed_updates="message")
    except Exception as e:
        print(f"[Telegram] Polling error: {e}")
        global _is_polling
        _is_polling = False


async def stop_polling():
    global _bot, _token, _is_polling, _task
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    if _bot:
        try:
            await _bot.close()
        except Exception:
            pass
    # Don't clear token so we can restart
    _is_polling = False


async def handle_message(message: types.Message):
    """인바운드 메시지 처리 — @이름 메시지 또는 /직원명 메시지 포맷"""
    if not message.text:
        return

    text = message.text.strip()
    chat_id = message.chat.id
    sender_name = message.from_user.full_name

    # ── 도움말 명령어 ────────────────────────────────
    if text == "/help" or text == "도움말":
        agents = _get_active_agents_sync()
        if not agents:
            await message.answer("활성화된 직원이 없습니다. 대시보드에서 추가하세요.")
            return
        agent_list = "\n".join([f"  • @{a.telegram_name} — {a.role}" for a in agents if a.telegram_name])
        reply = f"""📋 **직원 호출 방법**\n\n메시지:\n"@이름 메시지 내용"\n\n예시:\n@김팀장 오늘 미팅 요약해줘\n\n---\n{agent_list}"""
        await message.answer(reply, parse_mode="Markdown")
        return

    # ── @telegram_name 메시지 패턴 매칭 ──────────────
    agents = _get_active_agents_sync()
    matched_agent: Optional[Agent] = None

    for agent in agents:
        if not agent.telegram_name:
            continue
        # @이름 or /이름 패턴
        prefix_at = f"@{agent.telegram_name}"
        prefix_slash = f"/{agent.telegram_name}"

        if text.startswith(prefix_at):
            matched_agent = agent
            user_prompt = text[len(prefix_at):].strip()
            break
        elif text.startswith(prefix_slash):
            matched_agent = agent
            user_prompt = text[len(prefix_slash):].strip()
            break

    if not matched_agent:
        # 직원 이름이 없으면 목록 보여줌
        agent_names = ", ".join([f"@{a.telegram_name}" for a in agents if a.telegram_name])
        if agent_names:
            await message.answer(f"❌ 알 수 없는 직원입니다. 사용 가능한 직원: {agent_names}\n\n도움말을 입력하면 자세한 사용법을 볼 수 있습니다.")
        return

    if not user_prompt:
        await message.answer(f"@{matched_agent.telegram_name} 뒤에 메시지를 입력해주세요.")
        return

    # ── Ollama 호출 ────────────────────────────────
    await message.answer(f"⏳ @{matched_agent.telegram_name}(이)가 작업을 시작합니다...")

    try:
        result = ollama.generate_response(
            model_name=matched_agent.model_name,
            system_prompt=matched_agent.system_prompt,
            user_prompt=user_prompt,
        )
    except Exception as e:
        result = f"[실행 오류] {e}"

    # ── 결과 전송 (긴 메시지는 분할) ─────────────────
    if len(result) > 4000:
        chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
        for chunk in chunks:
            await message.answer(chunk)
    else:
        await message.answer(f"**@{matched_agent.telegram_name}의 응답:**\n\n{result}", parse_mode="Markdown")


def _get_active_agents_sync() -> list[Agent]:
    """동기적으로 활성 Agent 목록 조회"""
    try:
        db = next(get_db())
        agents = db.query(Agent).filter_by(deleted_at=None, is_active=True).all()
        db.close()
        return agents
    except Exception as e:
        print(f"[Telegram] Failed to get agents: {e}")
        return []
