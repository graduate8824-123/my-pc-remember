import React, { useState } from 'react';
import { Folder, Trash2, Plus, X, FolderOpen, Check } from 'lucide-react';
import { FolderItem } from '../types';

interface FolderSelectorProps {
  folders: FolderItem[];
  onAddFolder: (path: string) => Promise<void>;
  onRemoveFolder: (id: number) => Promise<void>;
  isOpen: boolean;
  onClose: () => void;
}

export const FolderSelector: React.FC<FolderSelectorProps> = ({
  folders,
  onAddFolder,
  onRemoveFolder,
  isOpen,
  onClose,
}) => {
  const [folderPath, setFolderPath] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!folderPath.trim()) return;

    try {
      setIsSubmitting(true);
      setError(null);
      await onAddFolder(folderPath.trim());
      setFolderPath('');
    } catch (err: any) {
      setError(err.message || 'Failed to add folder');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUseDemo = async () => {
    setFolderPath('data/sample_documents/DSA');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-xs p-4">
      <div className="bg-white rounded border border-neutral-300 w-full max-w-lg shadow-sm">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-neutral-200">
          <div>
            <h2 className="text-sm font-semibold text-neutral-900">
              Manage Indexed Folders
            </h2>
            <p className="text-xs text-neutral-500">
              Select specific directories to include in your local semantic memory.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-neutral-400 hover:text-neutral-600 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5">
          {/* Add folder form */}
          <form onSubmit={handleSubmit} className="mb-5">
            <label className="block text-xs font-medium text-neutral-700 mb-1.5">
              Folder Path
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={folderPath}
                onChange={(e) => setFolderPath(e.target.value)}
                placeholder="/Users/username/Documents/DSA or data/sample_documents/DSA"
                className="flex-1 px-3 py-2 text-xs font-mono border border-neutral-300 rounded focus:border-neutral-900 focus:outline-none"
              />
              <button
                type="submit"
                disabled={!folderPath.trim() || isSubmitting}
                className="px-3.5 py-2 text-xs font-medium text-white bg-neutral-900 hover:bg-neutral-800 disabled:opacity-50 rounded transition-colors shrink-0"
              >
                {isSubmitting ? 'Scanning...' : '+ Add'}
              </button>
            </div>

            <div className="flex items-center justify-between mt-1.5">
              <button
                type="button"
                onClick={handleUseDemo}
                className="text-[11px] text-neutral-500 hover:text-neutral-900 underline"
              >
                Insert sample demo folder (DSA Notes)
              </button>
            </div>

            {error && (
              <p className="text-xs text-red-600 mt-2">
                {error}
              </p>
            )}
          </form>

          {/* Current Folders list */}
          <div>
            <h3 className="text-xs font-medium text-neutral-700 mb-2">
              Indexed Folders ({folders.length})
            </h3>

            {folders.length === 0 ? (
              <div className="text-xs text-neutral-400 py-3 text-center border border-dashed border-neutral-200 rounded">
                No folders added yet. Add a directory above to begin indexing.
              </div>
            ) : (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {folders.map((f) => (
                  <div
                    key={f.id}
                    className="flex items-center justify-between p-2.5 bg-neutral-50 border border-neutral-200 rounded text-xs"
                  >
                    <div className="min-w-0 pr-3">
                      <div className="flex items-center gap-1.5 font-medium text-neutral-800">
                        <FolderOpen className="w-3.5 h-3.5 text-neutral-600 shrink-0" />
                        <span className="truncate font-mono">{f.path}</span>
                      </div>
                      <div className="text-[11px] text-neutral-500 mt-0.5 pl-5">
                        {f.file_count} files
                        {f.last_scanned_at && ` · Last scanned: ${new Date(f.last_scanned_at).toLocaleTimeString()}`}
                      </div>
                    </div>

                    <button
                      onClick={() => onRemoveFolder(f.id)}
                      className="p-1.5 text-neutral-400 hover:text-red-600 hover:bg-white rounded transition-colors shrink-0"
                      title="Remove folder from index"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-neutral-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
