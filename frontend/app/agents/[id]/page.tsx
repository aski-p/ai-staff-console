import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { agentsApi, permsApi } from "../lib/api";
import type { Agent, Permission } from "../lib/types";

export default function AgentDetailPage() {
  const { id: routeId } = useParams();
  const aid = Number(routeId);
  const [agent, setAgent] = useState<Agent | null>(null);
  const [perms, setPerms] = useState<Permission | null>(null);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    Promise.all([agentsApi.get(aid), permsApi.get(aid)]).then(([a, p]) => {
      setAgent(a);
      setPerms(p);
    });
  }, [aid]);

  async function updatePerm(field: keyof Permission, value: boolean) {
    await permsApi.update(aid, { [field]: value });
    setPerms(prev => prev ? { ...prev, [field]: value } : null);
  }

  async function saveAgent() {
    // agent is already updated in local state
    await agentsApi.update(aid, { name: agent?.name, role: agent?.role, model_name: agent?.model_name });
    setEditMode(false);
  }

  if (!agent || !perms) return <div className="empty-state">로딩 중...</div>;

  const permsList = [
    { key: "can_read_files" as any, label: "파일 읽기", danger: false },
    { key: "can_write_files" as any, label: "파일 쓰기", danger: true },
    { key: "can_execute_shell" as any, label: "쉘 실행", danger: true },
    { key: "can_use_internet" as any, label: "인터넷 접근", danger: true },
    { key: "can_access_medical_rag" as any, label: "의료 RAG 접근", danger: false },
    { key: "can_access_insurance_rag" as any, label: "보험 RAG 접근", danger: false },
    { key: "can_access_dailywon_rag" as any, label: "DailyWon RAG 접근", danger: false },
    { key: "can_access_code_rag" as any, label: "코드 RAG 접근", danger: false },
  ];

  return (
    <>
      <h2>직원 상세 - {agent.name}</h2>
      <div className="card">
        <div style={{display:"grid", gap:"1rem"}}>
          <p><strong>역할:</strong> {agent.role}</p>
          <p><strong>모델:</strong> <span className="badge badge-blue">{agent.model_name}</span></p>
          <p><strong>상태:</strong> <span className={`badge ${agent.is_active ? "badge-green" : "badge-gray"}`}>{agent.is_active ? "활성" : "비활성"}</span></p>
          <p><strong>생성일:</strong> {new Date(agent.created_at).toLocaleString("ko-KR")}</p>
        </div>

        {!editMode ? (
          <>
            <p style={{marginTop:"1rem"}}><strong>시스템 프롬프트:</strong></p>
            <pre style={{background:"#f3f4f6", padding:"1rem", borderRadius:"0.5rem", whiteSpace:"pre-wrap", fontSize:"0.85rem"}}>{agent.system_prompt}</pre>
            <button className="btn btn-primary mt-1" onClick={() => setEditMode(true)}>편집</button>
          </>
        ) : (
          <>
            <div className="form-group"><label>이름</label><input value={agent.name} onChange={e => setAgent({...agent, name: e.target.value})}/></div>
            <div className="form-group"><label>역할</label><input value={agent.role} onChange={e => setAgent({...agent, role: e.target.value})}/></div>
            <div className="form-group"><label>모델</label>
              <select value={agent.model_name as string} onChange={e => setAgent({...agent, model_name: e.target.value})}>
                <option value="qwen3-coder">qwen3-coder</option>
                <option value="qwen3.6:27b">qwen3.6:27b</option>
              </select>
            </div>
            <button className="btn btn-success" onClick={saveAgent}>저장</button>
            <button className="btn mt-1" onClick={() => setEditMode(false)}>취소</button>
          </>
        )}
      </div>

      <h2>권한 관리</h2>
      <div className="card">
        {permsList.map(p => (
          <label key={p.key} className={`checkbox-row ${p.danger ? "danger-perm" : ""}`}>
            <input type="checkbox" checked={perms[p.key]} onChange={e => updatePerm(p.key, e.target.checked)} />
            {p.label} {p.danger && "⚠️"}
          </label>
        ))}
      </div>
    </>
  );
}
