"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { tasksApi, agentsApi, ragApi } from "../lib/api";
import type { Agent, RagCollection } from "../lib/types";

export default function NewTaskPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [rags, setRags] = useState<any[]>([]);
  const [form, setForm] = useState({ agent_id: "", title: "", prompt: "", selected_rags: [] as number[] });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([agentsApi.list(), ragApi.list()]).then(([a, r]) => {
      setAgents(a as Agent[]);
      setRags(r as any[]);
    });
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.agent_id || !form.title || !form.prompt) return;
    setSubmitting(true);
    try {
      await tasksApi.create({ agent_id: Number(form.agent_id), title: form.title, prompt: form.prompt, rag_collections: form.selected_rags });
      router.push("/tasks");
    } catch (err) { alert("작업 생성 실패: " + err); }
    finally { setSubmitting(false); }
  }

  function toggleRag(id: number) {
    setForm(prev => ({ ...prev, selected_rags: prev.selected_rags.includes(id) ? prev.selected_rags.filter(x => x !== id) : [...prev.selected_rags, id] }));
  }

  return (
    <>
      <h2>새 작업 생성</h2>
      <div className="card" style={{maxWidth:"640px"}}>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>대상 직원</label>
            <select value={form.agent_id} onChange={e => setForm({...form, agent_id: e.target.value})} required>
              <option value="">선택...</option>
              {agents.filter(a => a.is_active).map(a => <option key={a.id} value={a.id}>{a.name} ({a.role})</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>작업 제목</label>
            <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
          </div>
          <div className="form-group">
            <label>작업 내용 (프롬프트)</label>
            <textarea value={form.prompt} onChange={e => setForm({...form, prompt: e.target.value})} rows={5} required />
          </div>
          <div className="form-group">
            <label>RAG 컬렉션 선택</label>
            {rags.map(r => (
              <label key={r.id} className="checkbox-row" style={{fontSize:"0.85rem"}}>
                <input type="checkbox" checked={form.selected_rags.includes(r.id)} onChange={() => toggleRag(r.id)} />
                {r.name} - {r.description || "설명 없음"}
              </label>
            ))}
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? "처리 중..." : "작업 생성"}</button>
          <a href="/tasks" style={{marginLeft:"0.5rem", color:"#6366f1", fontSize:"0.85rem"}}>취소</a>
        </form>
      </div>
    </>
  );
}
