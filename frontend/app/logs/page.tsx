"use client";
import { useEffect, useState } from "react";
import { logsApi } from "@/app/lib/api";

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    logsApi.list().then((l) => {
      setLogs(l as any[]);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="empty-state">로딩 중...</div>;

  return (
    <>
      <h2>작업 로그</h2>
      <div className="card">
        {logs.length === 0 ? (
          <p className="empty-state">로그가 없습니다</p>
        ) : (
          <table>
            <thead><tr><th>ID</th><th>직원</th><th>동작</th><th>세부 사항</th><th>시간</th></tr></thead>
            <tbody>
              {logs.map(l => (
                <tr key={l.id}>
                  <td>{l.id}</td>
                  <td>{l.agent_name || "-"}</td>
                  <td><span className="badge badge-blue">{l.action}</span></td>
                  <td style={{maxWidth:"300px", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap"}}>{l.details}</td>
                  <td>{new Date(l.created_at).toLocaleString("ko-KR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
