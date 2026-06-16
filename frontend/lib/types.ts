export interface Agent {
  id: number; name: string; role: string; description: string;
  system_prompt: string; model_name: string; telegram_name: string | null;
  is_active: boolean; requires_approval: boolean; created_at: string; deleted_at: string | null;
}

export interface Permission {
  id: number; agent_id: number;
  can_read_files: boolean; can_write_files: boolean;
  can_execute_shell: boolean; can_use_internet: boolean;
  can_access_medical_rag: boolean; can_access_insurance_rag: boolean;
  can_access_dailywon_rag: boolean; can_access_code_rag: boolean;
}

export interface RagCollection {
  id: number; name: string; description: string; collection_path: string;
  agent_ids: any[] | string; document_count: number; created_at: string;
}

export interface Task {
  id: number; agent_id: number; title: string; prompt: string;
  rag_collections: any[] | string; status: string; result: string;
  error_message: string; started_at: string | null; completed_at: string | null;
  created_at: string;
}

export interface Log {
  id: number; task_id: number | null; agent_id: number | null;
  agent_name: string; action: string; details: string;
  permissions_used: any; created_at: string;
}

export interface DashboardStats {
  total_agents: number; active_agents: number;
  rag_collections: number; pending_tasks: number;
}

export const STATUS_LABELS: Record<string, string> = {
  pending: "대기 중", running: "실행 중", completed: "완료",
  waiting_approval: "승인 대기", failed: "반려됨",
};
