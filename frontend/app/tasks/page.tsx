"use client";
import { useEffect, useState } from "react";
import { tasksApi, agentsApi } from "../lib/api";
import type { Task, Agent } from "../lib/types";
import { STATUS_LABELS } from "../lib/types";

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, [filter]);

  async function loadData() {
    setLoading(true);
    const [t, a] = await Promise.all([
      filter ? tasksApi.list(filter) : tasksApi.list(),
      agentsApi.list(),
    ]);
    setTasks(t as Task[]);
    setAgents(a as Agent[]);
    setLoading(false);
  }

  return (
    <>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h2>작업 지시</h2>
        <a href="/tasks/new" className="btn btn-primary">+ 작업 생성</a>
      </div>

      <div style={{marginBottom:1}}>
        <select value={filter} onChange={e => setFilter(e.target.value)} style={{width:"auto", display:"inline-block"}}>
          <option value="">전체</option>
          <option value="pending">대기 중</option>
          <option value="running">실행 중</option>
          <option value="completed">완료</option>
          <option value="waiting_approval">승인 대기</option>
          <option value="failed">반려됨</option>
        </select>
      </div>

      {loading ? <p className="empty-state">로딩 중...</p> : (
        <div className="card">
          <table>
            <thead><tr><th>ID</th><th>제목</th><th>상태</th><th>생성 시간</th><th>작업</th></tr></thead>
            <tbody>
              {tasks.map(t => (
                <tr key={t.id}>
                  <td>{t.id}</td>
                  <td><a href={`/tasks/${t.id}`} style={{color:"#6366f1"}}>{t.title}</a></td>
                  <td><span className={`badge ${statusBadge(t.status)}`}>{STATUS_LABELS[t.status] ?? t.status}</span></td>
                  <td>{new Date(t.created_at).toLocaleString("ko-KR")}</td>
                  <td><a href={`/tasks/${t.id}`} className="btn btn-sm">자세히</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function statusBadge(s: string) {
  if (s === "pending") return "badge-yellow";
  if (s === "completed") return "badge-green";
  if (s === "waiting_approval") return "badge-yellow";
  if (s === "failed") return "badge-red";
  if (s === "running") return "badge-blue";
  return "badge-gray";
}
