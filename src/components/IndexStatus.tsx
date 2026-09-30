import React from 'react';
import { RefreshCw, FolderPlus, AlertCircle, CheckCircle2 } from 'lucide-react';
import { IndexStatusResponse } from '../types';

interface IndexStatusProps {
  status: IndexStatusResponse | null;
  onRefresh: () => void;
  onReindex: () => void;
  onAddFolderClick: () => void;
  isLoading: boolean;
}

export const IndexStatus: React.FC<IndexStatusProps> = ({
  status,
  onRefresh,
  onReindex,
  onAddFolderClick,
  isLoading,
}) => {
  if (!status) {
    return (
      <div className="py-2 text-xs text-neutral-400">
        Connecting to local index...
      </div>
    );
  }

  const isIndexing = status.is_indexing;

  return (
    <div className="border border-neutral-200 rounded bg-white p-3.5 mb-6 text-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Statistics Line */}
        <div className="flex flex-wrap items-center gap-2 text-xs text-neutral-700">
          <span className="font-semibold text-neutral-900">Indexed:</span>
          <span>{status.total_files} files</span>
          <span aria-hidden="true" className="text-neutral-300">·</span>
          <span>{status.total_documents} documents</span>
          <span aria-hidden="true" className="text-neutral-300">·</span>
          <span>{status.total_code} code files</span>
          <span aria-hidden="true" className="text-neutral-300">·</span>
          <span className="text-neutral-500">{status.total_chunks} chunks</span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onAddFolderClick}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-neutral-700 border border-neutral-200 rounded hover:bg-neutral-50 transition-colors"
          >
            <FolderPlus className="w-3.5 h-3.5" />
            + Add Folder
          </button>

          <button
            onClick={onReindex}
            disabled={isIndexing || isLoading}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-neutral-700 border border-neutral-200 rounded hover:bg-neutral-50 disabled:opacity-50 transition-colors"
            title="Scan for new or modified files"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isIndexing ? 'animate-spin' : ''}`} />
            {isIndexing ? 'Scanning...' : 'Re-index'}
          </button>
        </div>
      </div>

      {/* Real-time Indexing Progress Banner */}
      {isIndexing && (
        <div className="mt-3 pt-3 border-t border-neutral-100">
          <div className="flex items-center justify-between text-xs text-neutral-600 mb-1.5">
            <span className="font-medium text-neutral-800">
              Indexing {status.current_file || 'files...'}
            </span>
            <span>
              {status.processed_count} processed · {status.skipped_count} skipped
              {status.failed_count > 0 && ` · ${status.failed_count} failed`}
            </span>
          </div>

          <div className="w-full bg-neutral-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-neutral-800 h-full transition-all duration-300"
              style={{ width: `${Math.max(5, Math.round(status.progress * 100))}%` }}
            />
          </div>
        </div>
      )}

      {/* Error notification if any files failed */}
      {!isIndexing && status.recent_errors && status.recent_errors.length > 0 && (
        <div className="mt-2.5 pt-2 text-xs text-amber-800 flex items-start gap-1.5 border-t border-neutral-100">
          <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <div>
            <span>Skipped {status.recent_errors.length} unreadable or unsupported file(s).</span>
          </div>
        </div>
      )}
    </div>
  );
};
