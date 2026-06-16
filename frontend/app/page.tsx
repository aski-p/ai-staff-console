"use client";
import { useEffect, useState } from "react";
import { dashboardApi, agentsApi, tasksApi } from "@/app/lib/api";
import type { DashboardStats, Agent, Task } from "@/app/lib/types";
import { STATUS_LABELS } from "@/app/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [recentTasks, setRecentTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardApi.stats(),
      agentsApi.list(),
      tasksApi.list(),
    ])
      .then(([s, a, t]) => {
        setStats(s as DashboardStats);
        setAgents(a as Agent[]);
        setRecentTasks((t as Task[]).slice(0, 5));
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">로딩 중...</div>;

  return (
    <>
      <h2>대시보드</h2>
      <div className="grid-2">
        <div className="stat-card">
          <span className="num">{stats?.total_agents ?? 0}</span>
          전체 AI 직원 수
        </div>
        <div className="stat-card green">
          <span className="num">{stats?.active_agents ?? 0}</span>
          활성 직원 수
        </div>
        <div className="stat-card amber">
          <span className="num">{stats?.rag_collections ?? 0}</span>
          RAG 컬렉션 수
        </div>
        <div className="stat-card rose">
          <span className="num">{stats?.pending_tasks ?? 0}</span>
          승인 대기 작업
        </div>
      </div>

      <h2 style={{marginTop: 2}}>최근 작업</h2>
      <div className="card">
        {recentTasks.length === 0 ? (
          <p className="empty-state">아직 작업이 없습니다</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th><th>제목</th><th>상태</th><th>생성 시간</th>
              </tr>
            </thead>
            <tbody>
              {recentTasks.map((t) => (
                <tr key={t.id}>
                  <td>{t.id}</td>
                  <td>{t.title}</td>
                  <td><span className={`badge ${statusBadge(t.status)}`}>{STATUS_LABELS[t.status] ?? t.status}</span></td>
                  <td>{new Date(t.created_at).toLocaleString("ko-KR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <h2>AI 직원 목록</h2>
      <div className="card">
        {agents.length === 0 ? (
          <p className="empty-state">직원이 없습니다</p>
        ) : (
          <table>
            <thead>
              <tr><th>ID</th><th>이름</th><th>역할</th><th>모델</th><th>상태</th></tr>
            </thead>
            <tbody>
              {agents.map((a) => (
                <tr key={a.id} style={{cursor: "pointer"}} onClick={() => window.location.href = `/agents/${a.id}`}>
                  <td>{a.id}</td>
                  <td>{a.name}</td>
                  <td>{a.role}</td>
                  <td className="badge badge-blue">{a.model_name}</td>
                  <td><span className={`badge ${a.is_active ? "badge-green" : "badge-gray"}`}>{a.is_active ? "활성" : "비활성"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

function statusBadge(status: string): string {
  switch (status) {
    case "pending": return "badge-yellow";
    case "running": return "badge-blue";
    case "completed": return "badge-green";
    case "waiting_approval": return "badge-yellow";
    case "failed": return "badge-red";
    default: return "badge-gray";
  }
}
