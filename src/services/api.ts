import {
  IndexStatusResponse,
  FolderItem,
  SearchResponse,
  SearchHistoryItem,
  FileDetail,
  SettingsResponse,
  HardwareInfo
} from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getIndexStatus(): Promise<IndexStatusResponse> {
    const res = await fetch(`${API_BASE}/index/status`);
    if (!res.ok) throw new Error('Failed fetching index status');
    return res.json();
  },

  async getFolders(): Promise<FolderItem[]> {
    const res = await fetch(`${API_BASE}/index/folders`);
    if (!res.ok) throw new Error('Failed fetching folders');
    return res.json();
  },

  async addFolder(path: string): Promise<FolderItem> {
    const res = await fetch(`${API_BASE}/index/folder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to add folder' }));
      throw new Error(err.detail || 'Failed to add folder');
    }
    return res.json();
  },

  async removeFolder(folderId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/index/folders/${folderId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed removing folder');
  },

  async startIndexing(folderId?: number, forceReindex: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/index/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_id: folderId, force_reindex: forceReindex }),
    });
    if (!res.ok) throw new Error('Failed to start indexing');
    return res.json();
  },

  async stopIndexing(): Promise<any> {
    const res = await fetch(`${API_BASE}/index/stop`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to stop indexing');
    return res.json();
  },

  async rebuildIndex(): Promise<any> {
    const res = await fetch(`${API_BASE}/index/rebuild`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to rebuild index');
    return res.json();
  },

  async search(query: string, topK: number = 8, useLLM: boolean = true): Promise<SearchResponse> {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK, use_llm_explanation: useLLM }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Search request failed' }));
      throw new Error(err.detail || 'Search request failed');
    }
    return res.json();
  },

  async getSearchHistory(): Promise<SearchHistoryItem[]> {
    const res = await fetch(`${API_BASE}/search/history`);
    if (!res.ok) throw new Error('Failed fetching search history');
    return res.json();
  },

  async clearSearchHistory(): Promise<void> {
    const res = await fetch(`${API_BASE}/search/history`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed clearing search history');
  },

  async getFileDetail(fileId: number): Promise<FileDetail> {
    const res = await fetch(`${API_BASE}/files/${fileId}`);
    if (!res.ok) throw new Error('Failed fetching file detail');
    return res.json();
  },

  async openFile(fileId: number): Promise<{ success: boolean; message: string; path: string }> {
    const res = await fetch(`${API_BASE}/files/${fileId}/open`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed opening file' }));
      throw new Error(err.detail || 'Failed opening file');
    }
    return res.json();
  },

  async getSettings(): Promise<SettingsResponse> {
    const res = await fetch(`${API_BASE}/settings`);
    if (!res.ok) throw new Error('Failed fetching settings');
    return res.json();
  },

  async updateSettings(payload: Partial<SettingsResponse>): Promise<SettingsResponse> {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed updating settings');
    return res.json();
  },

  async getHardwareInfo(): Promise<HardwareInfo> {
    const res = await fetch(`${API_BASE}/settings/hardware`);
    if (!res.ok) throw new Error('Failed fetching hardware info');
    return res.json();
  },
};
