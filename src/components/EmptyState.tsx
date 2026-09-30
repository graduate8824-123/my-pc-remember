import React from 'react';
import { HardDrive, FolderPlus, ShieldCheck, Cpu } from 'lucide-react';

interface EmptyStateProps {
  onAddFolder: () => void;
  onUseSampleFolder: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  onAddFolder,
  onUseSampleFolder,
}) => {
  return (
    <div className="border border-neutral-200 rounded bg-white p-10 text-center max-w-xl mx-auto my-8">
      <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4 text-neutral-800">
        <HardDrive className="w-6 h-6" />
      </div>

      <h2 className="text-base font-semibold text-neutral-900 mb-1.5">
        Your computer doesn't have a memory yet.
      </h2>
      
      <p className="text-xs text-neutral-500 mb-6 max-w-sm mx-auto leading-relaxed">
        Select a folder to start building your private local index.
        Your files never leave your computer.
      </p>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-8">
        <button
          onClick={onAddFolder}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 text-xs font-medium text-white bg-neutral-900 hover:bg-neutral-800 rounded transition-colors"
        >
          <FolderPlus className="w-4 h-4" />
          + Add Folder
        </button>

        <button
          onClick={onUseSampleFolder}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 text-xs font-medium text-neutral-700 bg-neutral-100 hover:bg-neutral-200 rounded border border-neutral-200 transition-colors"
        >
          Index Demo Folder (DSA Notes & Code)
        </button>
      </div>

      {/* Architecture Highlights */}
      <div className="grid grid-cols-2 gap-4 text-left border-t border-neutral-100 pt-6">
        <div className="flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-neutral-700 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-xs font-medium text-neutral-900">Zero Cloud Uploads</h3>
            <p className="text-[11px] text-neutral-500 leading-normal">
              100% local text extraction, FAISS vector indexing, and embedding.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2.5">
          <Cpu className="w-4 h-4 text-neutral-700 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-xs font-medium text-neutral-900">Hardware Agnostic</h3>
            <p className="text-[11px] text-neutral-500 leading-normal">
              Runs on Apple Silicon M1 (8GB RAM), ready for Snapdragon NPU.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
