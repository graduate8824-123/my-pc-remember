import React, { useState, useEffect } from 'react';
import { ShieldCheck, Cpu, HardDrive, AlertTriangle, Save, RefreshCw, Check } from 'lucide-react';
import { SettingsResponse, HardwareInfo, FolderItem } from '../types';
import { api } from '../services/api';

interface SettingsPanelProps {
  folders: FolderItem[];
  onOpenFolderManager: () => void;
  onRebuildIndex: () => void;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  folders,
  onOpenFolderManager,
  onRebuildIndex,
}) => {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [hardware, setHardware] = useState<HardwareInfo | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [embeddingModel, setEmbeddingModel] = useState('');
  const [llmProvider, setLlmProvider] = useState('mock');
  const [llmModel, setLlmModel] = useState('llama3.2:1b');
  const [ollamaUrl, setOllamaUrl] = useState('http://127.0.0.1:11434');
  const [topK, setTopK] = useState(8);
  const [chunkSize, setChunkSize] = useState(700);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const [sData, hData] = await Promise.all([
        api.getSettings(),
        api.getHardwareInfo(),
      ]);
      setSettings(sData);
      setHardware(hData);
      setEmbeddingModel(sData.embedding_model);
      setLlmProvider(sData.llm_provider);
      setLlmModel(sData.llm_model);
      setOllamaUrl(sData.ollama_base_url);
      setTopK(sData.top_k);
      setChunkSize(sData.chunk_size);
    } catch (err: any) {
      setError(err.message || 'Failed to load configuration');
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      setError(null);
      await api.updateSettings({
        embedding_model: embeddingModel,
        llm_provider: llmProvider,
        llm_model: llmModel,
        ollama_base_url: ollamaUrl,
        top_k: topK,
        chunk_size: chunkSize,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  if (!settings || !hardware) {
    return (
      <div className="py-8 text-center text-xs text-neutral-400">
        Loading configuration...
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-base font-semibold text-neutral-900">
          System & AI Settings
        </h2>
        <p className="text-xs text-neutral-500">
          Configure local models, vector chunking parameters, and hardware targets.
        </p>
      </div>

      {/* Privacy Notice */}
      <div className="border border-neutral-200 bg-neutral-50 rounded p-4 flex items-start gap-3">
        <ShieldCheck className="w-4 h-4 text-neutral-800 shrink-0 mt-0.5" />
        <div className="text-xs">
          <h3 className="font-semibold text-neutral-900 mb-0.5">Privacy Notice</h3>
          <p className="text-neutral-600 leading-relaxed">
            {settings.privacy_notice}
          </p>
          <p className="text-neutral-500 text-[11px] mt-1">
            Zero telemetry. SQLite metadata and FAISS vector indices reside exclusively in <span className="font-mono">{settings.database_path}</span>.
          </p>
        </div>
      </div>

      {/* Settings Form */}
      <form onSubmit={handleSave} className="border border-neutral-200 bg-white rounded p-5 space-y-5">
        {/* Local Embedding Model */}
        <div>
          <label className="block text-xs font-semibold text-neutral-800 mb-1">
            Embedding Model (Local Quantized ONNX / FastEmbed)
          </label>
          <input
            type="text"
            value={embeddingModel}
            onChange={(e) => setEmbeddingModel(e.target.value)}
            className="w-full px-3 py-2 text-xs font-mono border border-neutral-300 rounded focus:border-neutral-900 outline-none"
          />
          <p className="text-[11px] text-neutral-500 mt-1">
            Default: <code className="font-mono text-neutral-700">BAAI/bge-small-en-v1.5</code> (384-dimensional, ~30MB memory footprint, optimized for CPU/NPU).
          </p>
        </div>

        {/* LLM Provider Selection */}
        <div>
          <label className="block text-xs font-semibold text-neutral-800 mb-1">
            Local LLM Provider
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setLlmProvider('mock')}
              className={`p-3 text-left border rounded transition-colors ${
                llmProvider === 'mock'
                  ? 'border-neutral-900 bg-neutral-50 text-neutral-900 font-medium'
                  : 'border-neutral-200 text-neutral-600 hover:border-neutral-300'
              }`}
            >
              <div className="text-xs font-semibold">Deterministic Mock Provider</div>
              <div className="text-[11px] text-neutral-500 mt-0.5">
                Fast, zero-RAM development fallback. Grounded in actual extracted text.
              </div>
            </button>

            <button
              type="button"
              onClick={() => setLlmProvider('ollama')}
              className={`p-3 text-left border rounded transition-colors ${
                llmProvider === 'ollama'
                  ? 'border-neutral-900 bg-neutral-50 text-neutral-900 font-medium'
                  : 'border-neutral-200 text-neutral-600 hover:border-neutral-300'
              }`}
            >
              <div className="text-xs font-semibold">Ollama Local Provider</div>
              <div className="text-[11px] text-neutral-500 mt-0.5">
                On-device LLM inference via local Ollama instance (e.g. Llama 3.2 1B).
              </div>
            </button>
          </div>
        </div>

        {/* Ollama options if selected */}
        {llmProvider === 'ollama' && (
          <div className="p-3 bg-neutral-50 border border-neutral-200 rounded space-y-3">
            <div>
              <label className="block text-xs font-medium text-neutral-700 mb-1">
                Ollama Base URL
              </label>
              <input
                type="text"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                placeholder="http://127.0.0.1:11434"
                className="w-full px-3 py-1.5 text-xs font-mono border border-neutral-300 rounded focus:border-neutral-900 outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-neutral-700 mb-1">
                Ollama Model Tag
              </label>
              <input
                type="text"
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                placeholder="llama3.2:1b"
                className="w-full px-3 py-1.5 text-xs font-mono border border-neutral-300 rounded focus:border-neutral-900 outline-none"
              />
            </div>
          </div>
        )}

        {/* Retrieval Parameters */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-neutral-100">
          <div>
            <label className="block text-xs font-semibold text-neutral-800 mb-1">
              Top K Results ({topK})
            </label>
            <input
              type="range"
              min="3"
              max="20"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full accent-neutral-900 cursor-pointer"
            />
            <span className="text-[11px] text-neutral-500">Max files surfaced per query</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-neutral-800 mb-1">
              Chunk Size ({chunkSize} tokens)
            </label>
            <input
              type="range"
              min="200"
              max="1500"
              step="50"
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              className="w-full accent-neutral-900 cursor-pointer"
            />
            <span className="text-[11px] text-neutral-500">Approx ~2800 characters</span>
          </div>
        </div>

        {error && (
          <p className="text-xs text-red-600">{error}</p>
        )}

        <div className="pt-2 flex items-center justify-between">
          <button
            type="submit"
            disabled={isSaving}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-white bg-neutral-900 hover:bg-neutral-800 rounded transition-colors"
          >
            {saveSuccess ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>Settings Saved</span>
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5" />
                <span>Save Configuration</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Snapdragon AI & Hardware Readiness Card */}
      <div className="border border-neutral-200 bg-white rounded p-5">
        <div className="flex items-center gap-2 mb-2">
          <Cpu className="w-4 h-4 text-neutral-800" />
          <h3 className="text-xs font-semibold text-neutral-900">
            Hardware Execution Profile & Snapdragon Architecture
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs mt-3 mb-4">
          <div className="p-3 bg-neutral-50 rounded border border-neutral-100">
            <span className="text-[11px] text-neutral-500 block">Host Platform</span>
            <span className="font-semibold text-neutral-800">{hardware.hardware_profile.hardware_target}</span>
            <span className="text-[11px] text-neutral-500 block mt-1">Active Backend</span>
            <span className="font-mono text-neutral-700">{hardware.inference_backend.backend}</span>
          </div>

          <div className="p-3 bg-neutral-50 rounded border border-neutral-100">
            <span className="text-[11px] text-neutral-500 block">Target Architecture</span>
            <span className="font-semibold text-neutral-800">Snapdragon X Elite / Hexagon NPU</span>
            <span className="text-[11px] text-neutral-500 block mt-1">Abstraction Layer</span>
            <span className="text-emerald-700 font-medium">Ready (InferenceBackend decoupled)</span>
          </div>
        </div>

        <p className="text-xs text-neutral-600 leading-relaxed">
          {hardware.inference_backend.notes}
        </p>
      </div>

      {/* Index Management & Maintenance */}
      <div className="border border-neutral-200 bg-white rounded p-5">
        <h3 className="text-xs font-semibold text-neutral-900 mb-1">
          Index Maintenance
        </h3>
        <p className="text-xs text-neutral-500 mb-3">
          Manage indexed folders or completely clear the FAISS vector database.
        </p>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={onOpenFolderManager}
            className="px-3 py-1.5 text-xs font-medium text-neutral-800 bg-neutral-100 hover:bg-neutral-200 rounded border border-neutral-200 transition-colors"
          >
            Manage Folders ({folders.length})
          </button>

          <button
            type="button"
            onClick={onRebuildIndex}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-neutral-800 hover:bg-neutral-100 rounded border border-neutral-200 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Rebuild Vector Index
          </button>
        </div>
      </div>
    </div>
  );
};
