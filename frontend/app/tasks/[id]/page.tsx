"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { tasksApi } from "../lib/api";
import type { Task } from "../lib/types";
import { STATUS_LABELS } from "../lib/types";

export default function TaskDetailPage() {
  const { id: routeId } = useParams();
  const tid = Number(routeId);
  const router = useRouter();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadTask(); }, [tid]);

  async function loadTask() {
    const t = await tasksApi.get(tid);
    setTask(t as Task);
    setLoading(false);
  }

  async function runTask() {
    await tasksApi.run(tid);
    loadTask();
  }

  async function approveTask() {
    if (confirm("이 작업 결과를 승인하시겠습니까?")) {
      await tasksApi.approve(tid);
      loadTask();
    }
  }

  async function rejectTask() {
    if (confirm("이 작업 결과를 반려하시겠습니까?")) {
      await tasksApi.reject(tid);
      loadTask();
    }
  }

  if (loading || !task) return <div className="empty-state">로딩 중...</div>;

  return (
    <>
      <h2>작업 상세 - {task.title}</h2>
      <div className="card">
        <p><strong>ID:</strong> {task.id} | <strong>상태:</strong> <span className={`badge ${statusBadge(task.status)}`}>{STATUS_LABELS[task.status] ?? task.status}</span></p>
        <p style={{marginTop:"0.5rem"}}><strong>프롬프트:</strong></p>
        <pre style={{background:"#f3f4f6", padding:"1rem", borderRadius:"0.5rem", whiteSpace:"pre-wrap", fontSize:"0.85rem"}}>{task.prompt}</pre>
        {task.result && (
          <>
            <p style={{marginTop:"1rem"}}><strong>결과:</strong></p>
            <pre style={{background:"#d1fae5", padding:"1rem", borderRadius:"0.5rem", whiteSpace:"pre-wrap", fontSize:"0.85rem"}}>{task.result}</pre>
          </>
        )}
        {task.error_message && (
          <>
            <p style={{marginTop:"0.5rem"}}><strong style={{color:"#dc2626"}}>오류:</strong></p>
            <pre style={{background:"#fee2e2", padding:"1rem", borderRadius:"0.5rem", fontSize:"0.85rem" }}>{task.error_message}</pre>
          </>
        )}

        <div style={{marginTop:"1rem"}}>
          {task.status === "pending" && <button onClick={runTask} className="btn btn-primary">실행</button>}
          {task.status === "waiting_approval" && (<>
            <button onClick={approveTask} className="btn btn-success">승인</button>
            <button onClick={rejectTask} className="btn btn-danger">반려</button>
          </>)}
          <a href="/tasks" style={{marginLeft:"0.5rem", color:"#6366f1"}}>&larr; 목록으로</a>
        </div>
      </div>
    </>
  );
}

function statusBadge(s: string) {
  if (s === "pending") return "badge-yellow";
  if (s === "completed") return "badge-green";
  if (s === "waiting_approval") return "badge-yellow";
  if (s === "failed") return "badge-red";
  return "badge-blue";
}
