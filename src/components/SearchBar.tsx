import React, { useRef, useEffect } from 'react';
import { Search, X, CornerDownLeft, Sparkles } from 'lucide-react';

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (q: string) => void;
  isLoading: boolean;
}

const SUGGESTIONS = [
  'Find the Dijkstra notes I worked on recently',
  'Find the code where I implemented minimum spanning tree using DSU',
  'I remember a PDF about graph algorithms',
  'Breadth-first search queue implementation',
  'dijkstra.cpp',
];

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  setQuery,
  onSearch,
  isLoading,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Keyboard shortcut Cmd+K or Ctrl+K
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="mb-6">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center border border-neutral-300 rounded focus-within:border-neutral-900 focus-within:ring-1 focus-within:ring-neutral-900 bg-white transition-all">
          <Search className="w-4 h-4 text-neutral-400 ml-3.5 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your files by what you remember, not what they're called..."
            className="w-full px-3 py-3 text-sm text-neutral-900 placeholder:text-neutral-400 bg-transparent outline-none"
            disabled={isLoading}
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="p-1 mr-1 text-neutral-400 hover:text-neutral-600 rounded"
              title="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="flex items-center gap-1.5 mr-2 px-3 py-1.5 text-xs font-medium text-white bg-neutral-900 hover:bg-neutral-800 disabled:opacity-40 rounded transition-colors"
          >
            {isLoading ? 'Searching...' : 'Search'}
            <CornerDownLeft className="w-3 h-3 opacity-60" />
          </button>
        </div>
      </form>

      {/* Suggested memory searches */}
      <div className="mt-2.5 flex flex-wrap items-center gap-1.5 text-xs">
        <span className="text-neutral-600 font-medium">Examples:</span>
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setQuery(item);
              onSearch(item);
            }}
            className="text-left px-2 py-0.5 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded border border-neutral-200 transition-colors"
          >
            "{item}"
          </button>
        ))}
      </div>
    </div>
  );
};
