import React, { useEffect, useState } from 'react';
import { X, FileText, Code2, Copy, Check, ExternalLink } from 'lucide-react';
import { SearchResultItem, FileDetail } from '../types';
import { api } from '../services/api';

interface ContextModalProps {
  result: SearchResultItem | null;
  onClose: () => void;
}

export const ContextModal: React.FC<ContextModalProps> = ({ result, onClose }) => {
  const [fileDetail, setFileDetail] = useState<FileDetail | null>(null);
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (result) {
      setIsLoading(true);
      api.getFileDetail(result.file_id)
        .then((detail) => setFileDetail(detail))
        .catch(() => setFileDetail(null))
        .finally(() => setIsLoading(false));
    } else {
      setFileDetail(null);
    }
  }, [result]);

  if (!result) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(result.matched_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpen = () => {
    api.openFile(result.file_id);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-xs p-4">
      <div className="bg-white rounded border border-neutral-300 w-full max-w-2xl max-h-[85vh] flex flex-col shadow-sm">
        {/* Header */}
        <div className="flex items-start justify-between px-5 py-4 border-b border-neutral-200">
          <div className="min-w-0 pr-4">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-neutral-700 shrink-0" />
              <h2 className="text-sm font-semibold text-neutral-900 truncate">
                {result.filename}
              </h2>
              <span className="text-xs font-mono text-neutral-500">
                ({Math.round(result.score * 100)}% relevant)
              </span>
            </div>
            <p className="text-xs text-neutral-400 font-mono truncate mt-0.5">
              {result.path}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1 text-neutral-400 hover:text-neutral-600 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 overflow-y-auto space-y-4">
          {/* Grounded explanation */}
          <div>
            <h3 className="text-xs font-medium text-neutral-700 mb-1">
              Why this matches your query
            </h3>
            <div className="text-xs text-neutral-800 bg-neutral-50 p-3 rounded border border-neutral-200 leading-relaxed">
              {result.reason}
            </div>
          </div>

          {/* Matched excerpt */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <h3 className="text-xs font-medium text-neutral-700">
                Matched Content Excerpt (Indexed Chunk)
              </h3>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-[11px] text-neutral-500 hover:text-neutral-900"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Excerpt</span>
                  </>
                )}
              </button>
            </div>
            <pre className="text-xs font-mono bg-neutral-900 text-neutral-100 p-4 rounded overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-60 border border-neutral-800">
              {result.matched_content}
            </pre>
          </div>

          {/* File Metadata Overview */}
          {fileDetail && (
            <div className="border-t border-neutral-100 pt-3 flex flex-wrap gap-4 text-xs text-neutral-500">
              <div>
                <span className="font-medium text-neutral-700">Words:</span> {fileDetail.word_count}
              </div>
              <div>
                <span className="font-medium text-neutral-700">Pages:</span> {fileDetail.page_count}
              </div>
              <div>
                <span className="font-medium text-neutral-700">Chunks:</span> {fileDetail.chunks_count}
              </div>
              {fileDetail.size && (
                <div>
                  <span className="font-medium text-neutral-700">Size:</span> {Math.round(fileDetail.size / 1024)} KB
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-neutral-200 flex items-center justify-between bg-neutral-50">
          <button
            onClick={handleOpen}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-neutral-800 bg-white hover:bg-neutral-100 rounded border border-neutral-200 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            Open in System Viewer
          </button>

          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium text-white bg-neutral-900 hover:bg-neutral-800 rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
