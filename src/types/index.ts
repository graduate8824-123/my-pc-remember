export interface FolderItem {
  id: number;
  path: string;
  added_at?: string;
  last_scanned_at?: string;
  file_count: number;
  status: string;
}

export interface SearchResultItem {
  file_id: number;
  filename: string;
  path: string;
  extension: string;
  score: number; // 0.0 - 1.0
  matched_content: string;
  reason: string;
  modified_at?: string;
  size?: number;
  chunks_matched: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
  total_found: number;
  time_taken_ms: number;
  llm_available: boolean;
  mode: string;
  note?: string;
}

export interface IndexStatusResponse {
  is_indexing: boolean;
  total_files: number;
  total_documents: number;
  total_code: number;
  total_chunks: number;
  indexed_folders: FolderItem[];
  current_file?: string | null;
  progress: number;
  processed_count: number;
  skipped_count: number;
  failed_count: number;
  recent_errors: string[];
}

export interface FileDetail {
  id: number;
  path: string;
  filename: string;
  extension: string;
  size: number;
  modified_at?: string;
  indexed_at?: string;
  status: string;
  word_count: number;
  page_count: number;
  content_preview: string;
  chunks_count: number;
}

export interface SearchHistoryItem {
  id: number;
  query: string;
  result_count: number;
  created_at: string;
}

export interface SettingsResponse {
  embedding_provider: string;
  embedding_model: string;
  llm_provider: string;
  llm_model: string;
  ollama_base_url: string;
  top_k: number;
  chunk_size: number;
  chunk_overlap: number;
  inference_target: string;
  database_path: string;
  vector_index_path: string;
  privacy_notice: string;
}

export interface HardwareInfo {
  hardware_profile: {
    os: string;
    machine: string;
    processor: string;
    is_mac_apple_silicon: boolean;
    is_snapdragon: boolean;
    active_device: string;
    npu_available: boolean;
    hardware_target: string;
    memory_friendly: boolean;
  };
  inference_backend: {
    backend: string;
    target: string;
    npu_accelerated: boolean;
    acceleration_provider?: string;
    notes: string;
  };
  local_only: boolean;
  snapdragon_readiness: string;
}
