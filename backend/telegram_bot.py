"""Telegram Bot 모듈 — aiogram 3.x 기반 polling + 메시지 핸들러"""

import os, json, asyncio
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from sqlalchemy.orm import Session

from database import get_db
from models import Agent
import ollama_client as ollama

# ── State ────────────────────────────────────────
_bot: Optional[Bot] = None
_token: Optional[str] = None
_is_polling: bool = False
_poll_task: Optional[asyncio.Task] = None

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
    stored_token = cfg.get("bot_token", "")
    masked = stored_token[:10] + "..." if stored_token else ""
    return {
        "bot_token": masked,
        "is_active": cfg.get("active", False),
        "polling": _is_polling,
    }


async def configure(bot_token: str, active: bool):
    """Bot 토큰 설정 + 활성/비활성 토글"""
    global _bot, _token, _is_polling, _poll_task

    if active and bot_token:
        # Already running with same token? skip
        if _token == bot_token and _is_polling:
            return
        
        # Restart if changing token
        if _poll_task:
            await stop_polling()

        _token = bot_token
        try:
            # Validate token first
            _bot = Bot(token=_token)
            me = await _bot.get_me()
            print(f"[Telegram] Bot @{me.username} connected")
            await start_polling_with_bot(_bot)
        except Exception as e:
            print(f"[Telegram] Bot init failed: {e}")
            _bot = None
            cfg = _load_config()
            cfg["active"] = False
            _save_config(cfg)
            raise ValueError(f"봇 토큰 오류: {e}")
    else:
        # Deactivate
        cfg = _load_config()
        cfg["active"] = False
        if bot_token:
            cfg["bot_token"] = bot_token
        _save_config(cfg)
        await stop_polling()


async def start_polling_with_bot(bot: Bot):
    global _is_polling, _poll_task
    
    if _is_polling and not _poll_task.done():
        return

    dp = Dispatcher()
    dp.message.register(handle_message)
    
    _poll_task = asyncio.create_task(_do_poll(dp, bot))
    _is_polling = True


async def _do_poll(dp: Dispatcher, bot: Bot):
    try:
        await dp.start_polling(bot, allowed_updates="message")
    except Exception as e:
        print(f"[Telegram] Polling error: {e}")
    finally:
        global _is_polling
        _is_polling = False


async def stop_polling():
    global _bot, _token, _is_polling, _poll_task
    
    if _poll_task and not _poll_task.done():
        _poll_task.cancel()
        try:
            await _poll_task
        except asyncio.CancelledError:
            pass
        _poll_task = None
    
    if _bot:
        try:
            await _bot.close()
        except Exception:
            pass
        _bot = None
    
    _is_polling = False


async def handle_message(message: Message):
    """인바운드 메시지 처리"""
    if not message.text:
        return

    text = message.text.strip()
    
    # ── 도움말 명령어 ────────────────────────────────
    if text in ("/help", "도움말"):
        agents = _get_active_agents_sync()
        named_agents = [a for a in agents if getattr(a, 'telegram_name', None)]
        if not named_agents:
            await message.answer("활성화된 직원이 없습니다. 대시보드에서 추가하세요.")
            return
        agent_list = "\n".join([f"  • @{getattr(a, 'telegram_name')} — {a.role}" for a in named_agents])
        reply = (
            f"📋 **직원 호출 방법**\n\n"
            f"메시지:\n\"@이름 메시지 내용\"\n\n"
            f"예시:\n@김팀장 오늘 미팅 요약해줘\n\n---\n{agent_list}"
        )
        await message.answer(reply, parse_mode="Markdown")
        return

    # ── @telegram_name 메시지 패턴 매칭 ──────────────
    agents = _get_active_agents_sync()
    matched_agent = None
    user_prompt = ""

    for agent in agents:
        tname = getattr(agent, 'telegram_name', None)
        if not tname:
            continue
        
        prefix_at = f"@{tname}"
        prefix_slash = f"/{tname}"

        if text.startswith(prefix_at):
            matched_agent = agent
            user_prompt = text[len(prefix_at):].strip()
            break
        elif text.startswith(prefix_slash):
            matched_agent = agent
            user_prompt = text[len(prefix_slash):].strip()
            break

    if not matched_agent:
        named_agents = [a for a in agents if getattr(a, 'telegram_name', None)]
        agent_names = ", ".join([f"@{getattr(a, 'telegram_name')}" for a in named_agents])
        if agent_names:
            await message.answer(
                f"❌ 알 수 없는 직원입니다.\n사용 가능한 직원: {agent_names}\n\n도움말을 입력하면 자세한 사용법을 볼 수 있습니다."
            )
        return

    if not user_prompt:
        tname = getattr(matched_agent, 'telegram_name', '')
        await message.answer(f"@{tname} 뒤에 메시지를 입력해주세요.")
        return

    # ── Ollama 호출 ────────────────────────────────
    tname = getattr(matched_agent, 'telegram_name', '')
    model_name = str(getattr(matched_agent, 'model_name', 'qwen3-coder') or 'qwen3-coder')
    system_prompt = str(getattr(matched_agent, 'system_prompt', '') or '')

    await message.answer(f"⏳ @{tname}(이)가 작업을 시작합니다...")

    try:
        result = ollama.generate_response(
            model_name=model_name,
            system_prompt=system_prompt,
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
        await message.answer(f"**@{tname}의 응답:**\n\n{result}", parse_mode="Markdown")


def _get_active_agents_sync() -> list:
    """동기적으로 활성 Agent 목록 조회"""
    try:
        db = next(get_db())
        agents = db.query(Agent).filter_by(deleted_at=None, is_active=True).all()
        db.close()
        return agents
    except Exception as e:
        print(f"[Telegram] Failed to get agents: {e}")
        return []
