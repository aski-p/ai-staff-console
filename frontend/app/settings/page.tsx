"use client";
import { useEffect, useState } from "react";
import { settingsApi } from "../lib/api";

export default function SettingsPage() {
  const [token, setToken] = useState("");
  const [active, setActive] = useState(false);
  const [polling, setPolling] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      const cfg = await settingsApi.getTelegram();
      setToken(cfg.bot_token?.replace(/...$/, "") || "");
      setActive(cfg.is_active || false);
      setPolling(cfg.polling || false);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    try {
      await settingsApi.setTelegram({ bot_token: token, active }).then(() => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      });
      
      const cfg = await settingsApi.getTelegram();
      setActive(cfg.is_active || false);
      setPolling(cfg.polling || false);
    } catch (e: any) {
      alert(`저장 오류: ${e.message}`);
    }
  }

  async function handleStop() {
    try {
      await settingsApi.stopTelegram();
      setPolling(false);
    } catch (e: any) {
      alert(`중지 오류: ${e.message}`);
    }
  }

  if (loading) return <p>로딩 중...</p>;

  return (
    <>
      <h2>⚙️ 설정</h2>

      <div className="card" style={{ maxWidth: "600px" }}>
        <h3 style={{ marginBottom: "1rem", color: "#6366f1" }}>📱 Telegram 연동</h3>

        <div style={{ padding: "12px", background: polling ? "#d4edda" : "#fff3cd", borderRadius: "8px", marginBottom: "1rem" }}>
          {polling 
            ? "✅ Telegram 봇 활성화됨 — 메시지를 받고 있습니다."
            : active
              ? "⚠️ 봇이 활성화되었으나 polling이 실행 중이 아닙니다."
              : "🔴 Telegram 연동이 비활성 상태입니다."}
        </div>

        <div className="form-group">
          <label>Bot Token</label>
          <input
            type="text"
            value={token}
            onChange={e => setToken(e.target.value)}
            placeholder="123456789:ABCdefGHIjklMNOpqRSTuvwxYZ"
          />
        </div>

        <div className="form-group">
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="checkbox"
              checked={active}
              onChange={e => setActive(e.target.checked)}
            />
            활성화
          </label>
        </div>

        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
          <button className="btn btn-primary" onClick={handleSave}>
            저장
          </button>
          
          {polling && (
            <button className="btn btn-danger" onClick={handleStop}>
              중지
            </button>
          )}
        </div>

        {saved && <p style={{ color: "green", marginTop: "0.5rem" }}>✅ 설정이 저장되었습니다.</p>}

        <div style={{ marginTop: "1.5rem", padding: "12px", background: "#f8f9fa", borderRadius: "8px" }}>
          <p style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>💡 사용 방법</p>
          <ol style={{ paddingLeft: "1.5rem", lineHeight: "1.6" }}>
            <li>@BotFather 에서 Telegram 봇 생성 후 토큰 복사</li>
            <li>위 토큰을 입력하고 활성화 체크</li>
            <li><strong>직원 추가 시</strong> "텔레그램 별명" 필드 입력 (예: 김팀장)</li>
            <li>Telegram에서 "<code>@김팀장 오늘 미팅 요약해줘</code>" 와 같이 호출</li>
          </ol>
        </div>
      </div>
    </>
  );
}
