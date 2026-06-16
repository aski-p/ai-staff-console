"use client";
import { useEffect, useState } from "react";
import { agentsApi, del as httpDel } from "@/app/lib/api";
import type { Agent } from "@/app/lib/types";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: "", role: "", description: "", system_prompt: "너는 유능한 AI 어시스턴트다.", model_name: "qwen3-coder", telegram_name: "", is_active: true, requires_approval: false });

  useEffect(() => { loadAgents(); }, []);

  async function loadAgents() {
    setAgents(await agentsApi.list());
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await agentsApi.create(newAgent);
    setShowForm(false);
    loadAgents();
  }

  async function toggleActive(a: Agent) {
    await agentsApi.update(a.id, { is_active: !a.is_active });
    loadAgents();
  }

  async function deleteAgent(id: number) {
    if (confirm("이 직원을 삭제하시겠습니까?")) {
      await httpDel(`agents/${id}`);
      loadAgents();
    }
  }

  return (
    <>
      <div className="flex gap-2 items-center" style={{justifyContent: "space-between"}}>
        <h2>AI 직원 목록</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>+ 직원 추가</button>
      </div>

      {showForm && (
        <div className="card">
          <form onSubmit={handleCreate}>
            <div className="form-group"><label>이름</label><input value={newAgent.name} onChange={e => setNewAgent({...newAgent, name: e.target.value})} required /></div>
            <div className="form-group"><label>역할</label><input value={newAgent.role} onChange={e => setNewAgent({...newAgent, role: e.target.value})} required /></div>
            <div className="form-group"><label>설명</label><textarea value={newAgent.description} onChange={e => setNewAgent({...newAgent, description: e.target.value})} />
            </div>
            <div className="form-group"><label>시스템 프롬프트</label><textarea value={newAgent.system_prompt} onChange={e => setNewAgent({...newAgent, system_prompt: e.target.value})} rows={3} /></div>
            <div className="form-group"><label>모델</label>
              <select value={newAgent.model_name as string} onChange={e => setNewAgent({...newAgent, model_name: e.target.value})}>
                <option value="qwen3-coder">qwen3-coder</option>
                <option value="qwen3.6:27b">qwen3.6:27b</option>
              </select>
            </div>
            <div className="form-group"><label>텔레그램 별명 (선택)</label><input value={newAgent.telegram_name || ""} onChange={e => setNewAgent({...newAgent, telegram_name: e.target.value})} placeholder="김팀장" /></div>
            <div style={{display:"flex", gap:"1rem"}}>
              <label className="checkbox-row"><input type="checkbox" checked={newAgent.is_active} onChange={e => setNewAgent({...newAgent, is_active: e.target.checked})} /> 활성</label>
              <label className="checkbox-row"><input type="checkbox" checked={newAgent.requires_approval} onChange={e => setNewAgent({...newAgent, requires_approval: e.target.checked})} /> 승인 필요</label>
            </div>
            <button type="submit" className="btn btn-primary mt-1">생성</button>
          </form>
        </div>
      )}

      <div className="card">
        <table>
          <thead><tr><th>ID</th><th>이름</th><th>역할</th><th>모델</th><th>승인 필요</th><th>상태</th><th>생성일</th><th>작업</th></tr></thead>
          <tbody>
            {agents.map(a => (
              <tr key={a.id}>
                <td>{a.id}</td>
                <td><a href={`/agents/${a.id}`} style={{color:"#6366f1"}}>{a.name}</a></td>
                <td>{a.role}</td>
                <td><span className="badge badge-blue">{a.model_name}</span></td>
                <td>{a.requires_approval ? "⚠️" : "-"}</td>
                <td><button onClick={() => toggleActive(a)} className={`btn btn-sm ${a.is_active ? "btn-success" : "btn-danger"}`}>{a.is_active ? "활성화" : "비활성"}</button></td>
                <td>{new Date(a.created_at).toLocaleDateString("ko-KR")}</td>
                <td><button onClick={() => deleteAgent(a.id)} className="btn btn-sm btn-danger">삭제</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
