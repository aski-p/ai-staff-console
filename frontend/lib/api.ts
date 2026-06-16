const BASE = "/api";

export async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`API error ${r.status}: ${r.statusText}`);
  return r.json();
}

export async function post<T>(path: string, body: any): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`API error ${r.status}: ${r.statusText}`);
  return r.json();
}

export async function put<T>(path: string, body: any): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`API error ${r.status}: ${r.statusText}`);
  return r.json();
}

export async function del(path: string): Promise<any> {
  const r = await fetch(`${BASE}${path}`, { method: "DELETE" });
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}

// Convenience wrappers
export const agentsApi = {
  list: () => get<any[]>("agents"),
  create: (d: any) => post<any>("agents", d),
  get: (id: number) => get<any>(`agents/${id}`),
  update: (id: number, d: any) => put<any>(`agents/${id}`, d),
  delete: (id: number) => del(`agents/${id}`),
};

export const permsApi = {
  get: (agentId: number) => get<any>(`permissions/${agentId}`),
  update: (agentId: number, d: any) => put<any>(`permissions/${agentId}`, d),
};

export const ragApi = {
  list: () => get<any[]>("rag-collections"),
  create: (d: any) => post<any>("rag-collections", d),
};

export const tasksApi = {
  list: (status?: string) => get<any[]>(`tasks${status ? `?status=${status}` : ""}`),
  create: (d: any) => post<any>("tasks", d),
  get: (id: number) => get<any>(`tasks/${id}`),
  run: (id: number) => post<any>(`tasks/${id}/run`, {}),
  approve: (id: number) => post<any>(`tasks/${id}/approve`, {}),
  reject: (id: number) => post<any>(`tasks/${id}/reject`, {}),
};

export const logsApi = { list: () => get<any[]>("/logs") };
export const dashboardApi = { stats: () => get<any>("/dashboard") };

export const settingsApi = {
  getTelegram: () => get<any>("/settings/telegram"),
  setTelegram: (d: any) => post<any>("/settings/telegram", d),
  stopTelegram: () => post<any>("/settings/telegram/stop", {}),
};
