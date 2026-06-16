"use client";
import { useEffect, useState } from "react";
import { ragApi } from "@/app/lib/api";
import type { RagCollection } from "@/app/lib/types";

export default function RagPage() {
  const [rags, setRags] = useState<RagCollection[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [newRag, setNewRag] = useState({ name: "", description: "", collection_path: "" });

  useEffect(() => { loadRags(); }, []);

  async function loadRags() {
    setRags(await ragApi.list());
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await ragApi.create({ ...newRag, agent_ids: [], document_count: 0 });
    setShowForm(false);
    loadRags();
  }

  return (
    <>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h2>RAG 컬렉션 관리</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>+ 컬렉션 추가</button>
      </div>

      {showForm && (
        <div className="card">
          <form onSubmit={handleCreate}>
            <div className="form-group"><label>컬렉션 이름</label><input value={newRag.name} onChange={e => setNewRag({...newRag, name: e.target.value})} required /></div>
            <div className="form-group"><label>설명</label><textarea value={newRag.description} onChange={e => setNewRag({...newRag, description: e.target.value})} /></div>
            <div className="form-group"><label>경로</label><input value={newRag.collection_path} onChange={e => setNewRag({...newRag, collection_path: e.target.value})} /></div>
            <button type="submit" className="btn btn-primary">생성</button>
          </form>
        </div>
      )}

      <div className="card">
        <table>
          <thead><tr><th>ID</th><th>이름</th><th>설명</th><th>경로</th><th>문서 수</th><th>생성일</th></tr></thead>
          <tbody>
            {rags.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td><span className="badge badge-blue">{r.name}</span></td>
                <td>{r.description || "-"}</td>
                <td style={{fontSize:"0.75rem"}}>{r.collection_path || "-"}</td>
                <td>{typeof r.document_count === "number" ? r.document_count : 0}</td>
                <td>{new Date(r.created_at).toLocaleDateString("ko-KR")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
