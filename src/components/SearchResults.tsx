import React from 'react';
import { SearchResult } from './SearchResult';
import { SearchResponse, SearchResultItem } from '../types';
import { Clock, Info } from 'lucide-react';

interface SearchResultsProps {
  response: SearchResponse;
  onShowContext: (result: SearchResultItem) => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  response,
  onShowContext,
}) => {
  const { results, query, time_taken_ms, total_found, note } = response;

  if (total_found === 0) {
    return (
      <div className="border border-neutral-200 rounded bg-white p-8 text-center">
        <p className="text-sm font-medium text-neutral-800 mb-1">
          No matches found for "{query}"
        </p>
        <p className="text-xs text-neutral-500 max-w-md mx-auto">
          Try describing concepts or terms you remember from the document (e.g., algorithms, keywords, concepts).
        </p>
      </div>
    );
  }

  return (
    <section>
      {/* Header with stats and fallback notification */}
      <div className="flex items-center justify-between mb-3 text-xs text-neutral-500">
        <h2 className="font-semibold text-neutral-900 text-sm">
          Results
        </h2>
        <div className="flex items-center gap-1.5 font-mono">
          <Clock className="w-3.5 h-3.5" />
          <span>{total_found} {total_found === 1 ? 'file' : 'files'} in {time_taken_ms}ms</span>
        </div>
      </div>

      {note && (
        <div className="mb-3 p-2.5 bg-neutral-50 border border-neutral-200 rounded text-xs text-neutral-600 flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-neutral-500 shrink-0" />
          <span>{note}</span>
        </div>
      )}

      {/* List of Results */}
      <div className="space-y-3">
        {results.map((result, idx) => (
          <SearchResult
            key={`${result.file_id}-${idx}`}
            result={result}
            rank={idx + 1}
            onShowContext={onShowContext}
          />
        ))}
      </div>
    </section>
  );
};
