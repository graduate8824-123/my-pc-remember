import React, { useState } from 'react';
import { FileText, Code2, ExternalLink, Eye, Check } from 'lucide-react';
import { SearchResultItem } from '../types';
import { api } from '../services/api';

interface SearchResultProps {
  result: SearchResultItem;
  rank: number;
  onShowContext: (result: SearchResultItem) => void;
}

export const SearchResult: React.FC<SearchResultProps> = ({
  result,
  rank,
  onShowContext,
}) => {
  const [isOpening, setIsOpening] = useState(false);
  const [openStatus, setOpenStatus] = useState<string | null>(null);

  const isCode = [
    '.cpp', '.c', '.py', '.java', '.js', '.ts', '.tsx', '.html', '.css', '.sql', '.sh'
  ].includes(result.extension.toLowerCase());

  const relevancePercent = Math.min(99, Math.round(result.score * 100));

  const handleOpenFile = async () => {
    try {
      setIsOpening(true);
      setOpenStatus(null);
      const res = await api.openFile(result.file_id);
      if (res.success) {
        setOpenStatus('Opened');
        setTimeout(() => setOpenStatus(null), 3000);
      } else {
        setOpenStatus('Viewer opened');
        setTimeout(() => setOpenStatus(null), 3000);
      }
    } catch (err: any) {
      setOpenStatus('Path ready');
      setTimeout(() => setOpenStatus(null), 3000);
    } finally {
      setIsOpening(false);
    }
  };

  return (
    <article className="border border-neutral-200 rounded bg-white p-4 transition-colors hover:border-neutral-300">
      {/* Header: Rank + Filename + Relevance score */}
      <div className="flex items-start justify-between gap-3 mb-1">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-mono text-neutral-400 font-medium">
            {rank}.
          </span>
          {isCode ? (
            <Code2 className="w-4 h-4 text-neutral-700 shrink-0" />
          ) : (
            <FileText className="w-4 h-4 text-neutral-700 shrink-0" />
          )}
          <h3 className="text-sm font-semibold text-neutral-900 truncate">
            {result.filename}
          </h3>
        </div>

        <div className="shrink-0 text-right">
          <span className="text-xs font-medium text-neutral-900 font-mono">
            {relevancePercent}% relevant
          </span>
        </div>
      </div>

      {/* File Path */}
      <div className="text-xs text-neutral-500 font-mono truncate mb-2.5 pl-6">
        {result.path}
      </div>

      {/* Why this matches */}
      <div className="pl-6 mb-3">
        <p className="text-xs font-medium text-neutral-700 mb-0.5">
          Why this matches:
        </p>
        <p className="text-xs text-neutral-600 leading-relaxed bg-neutral-50 p-2.5 rounded border border-neutral-100">
          {result.reason}
        </p>
      </div>

      {/* Action buttons */}
      <div className="pl-6 flex items-center gap-2">
        <button
          onClick={handleOpenFile}
          disabled={isOpening}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-neutral-800 bg-neutral-100 hover:bg-neutral-200 rounded border border-neutral-200 transition-colors"
        >
          {openStatus ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span>{openStatus}</span>
            </>
          ) : (
            <>
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Open File</span>
            </>
          )}
        </button>

        <button
          onClick={() => onShowContext(result)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50 rounded border border-neutral-200 transition-colors"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Show Context</span>
        </button>

        {result.modified_at && (
          <span className="text-[11px] text-neutral-400 ml-auto hidden sm:inline">
            Modified: {new Date(result.modified_at).toLocaleDateString()}
          </span>
        )}
      </div>
    </article>
  );
};
