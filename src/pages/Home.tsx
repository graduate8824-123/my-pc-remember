import React, { useCallback, useEffect, useRef, useState } from 'react';
import { SearchBar } from '../components/SearchBar';
import { IndexStatus } from '../components/IndexStatus';
import { SearchResults } from '../components/SearchResults';
import { EmptyState } from '../components/EmptyState';
import { FolderSelector } from '../components/FolderSelector';
import { ContextModal } from '../components/ContextModal';
import {
  SearchResponse,
  IndexStatusResponse,
  SearchResultItem,
  SearchHistoryItem,
} from '../types';
import { api } from '../services/api';
import { Clock, Trash2 } from 'lucide-react';

export const Home: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] =
    useState<SearchResponse | null>(null);

  const [indexStatus, setIndexStatus] =
    useState<IndexStatusResponse | null>(null);

  const [searchHistory, setSearchHistory] =
    useState<SearchHistoryItem[]>([]);

  const [selectedContext, setSelectedContext] =
    useState<SearchResultItem | null>(null);

  const [isFolderManagerOpen, setIsFolderManagerOpen] = useState(false);

  const [isSearching, setIsSearching] = useState(false);

  const [isLoadingStatus, setIsLoadingStatus] = useState(false);

  // Prevent multiple searches from running at the same time
  const searchInProgressRef = useRef(false);

  // Prevent state updates after component unmount
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  /**
   * Load current indexing status
   */
  const loadStatus = useCallback(async () => {
    try {
      setIsLoadingStatus(true);

      const status = await api.getIndexStatus();

      if (mountedRef.current) {
        setIndexStatus(status);
      }
    } catch (err) {
      console.error('Failed loading index status:', err);
    } finally {
      if (mountedRef.current) {
        setIsLoadingStatus(false);
      }
    }
  }, []);

  /**
   * Load recent search history
   */
  const loadHistory = useCallback(async () => {
    try {
      const history = await api.getSearchHistory();

      if (mountedRef.current) {
        setSearchHistory(history);
      }
    } catch (err) {
      console.error('Failed loading search history:', err);
    }
  }, []);

  /**
   * Initial data loading
   */
  useEffect(() => {
    let cancelled = false;

    const initialize = async () => {
      try {
        const [status, history] = await Promise.all([
          api.getIndexStatus(),
          api.getSearchHistory(),
        ]);

        if (!cancelled && mountedRef.current) {
          setIndexStatus(status);
          setSearchHistory(history);
        }
      } catch (err) {
        console.error('Failed initializing home page:', err);
      }
    };

    initialize();

    return () => {
      cancelled = true;
    };
  }, []);

  /**
   * Poll index status while indexing is running.
   *
   * IMPORTANT:
   * This does NOT depend on isSearching.
   */
  useEffect(() => {
    if (!indexStatus?.is_indexing) {
      return;
    }

    let cancelled = false;

    const interval = window.setInterval(async () => {
      try {
        const status = await api.getIndexStatus();

        if (!cancelled && mountedRef.current) {
          setIndexStatus(status);
        }
      } catch (err) {
        // Ignore temporary polling failures.
        console.warn('Index status polling failed:', err);
      }
    }, 2500);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [indexStatus?.is_indexing]);

  /**
   * Search
   */
  const handleSearch = useCallback(
    async (searchQuery: string) => {
      const trimmedQuery = searchQuery.trim();

      if (!trimmedQuery) {
        return;
      }

      // Prevent duplicate simultaneous searches
      if (searchInProgressRef.current) {
        return;
      }

      try {
        searchInProgressRef.current = true;
        setIsSearching(true);

        const response = await api.search(trimmedQuery);

        if (mountedRef.current) {
          setSearchResults(response);
          setQuery(trimmedQuery);
        }

        // Refresh history after search
        await loadHistory();
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        searchInProgressRef.current = false;

        if (mountedRef.current) {
          setIsSearching(false);
        }
      }
    },
    [loadHistory]
  );

  /**
   * Add folder
   */
  const handleAddFolder = useCallback(
    async (path: string) => {
      try {
        await api.addFolder(path);
        await loadStatus();
      } catch (err) {
        console.error('Failed adding folder:', err);
      }
    },
    [loadStatus]
  );

  /**
   * Remove folder
   */
  const handleRemoveFolder = useCallback(
    async (folderId: number) => {
      try {
        await api.removeFolder(folderId);
        await loadStatus();
      } catch (err) {
        console.error('Failed removing folder:', err);
      }
    },
    [loadStatus]
  );

  /**
   * Start reindexing
   */
  const handleReindex = useCallback(async () => {
    try {
      await api.startIndexing(undefined, true);
      await loadStatus();
    } catch (err) {
      console.error('Failed starting indexing:', err);
    }
  }, [loadStatus]);

  /**
   * Clear search history
   */
  const handleClearHistory = useCallback(async () => {
    try {
      await api.clearSearchHistory();

      if (mountedRef.current) {
        setSearchHistory([]);
      }
    } catch (err) {
      console.error('Failed clearing search history:', err);
    }
  }, []);

  /**
   * Load demo/sample documents
   */
  const handleUseDemo = useCallback(async () => {
    try {
      await api.addFolder('data/sample_documents/DSA');
      await loadStatus();
    } catch (err) {
      console.error('Failed loading demo folder:', err);
    }
  }, [loadStatus]);

  /**
   * Determine whether files are indexed
   */
  const hasFiles =
    indexStatus !== null && indexStatus.total_files > 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">

      {/* =========================
          INDEX STATUS
      ========================== */}
      <IndexStatus
        status={indexStatus}
        onRefresh={loadStatus}
        onReindex={handleReindex}
        onAddFolderClick={() => setIsFolderManagerOpen(true)}
        isLoading={isLoadingStatus}
      />

      {/* =========================
          SEARCH
      ========================== */}
      <SearchBar
        query={query}
        setQuery={setQuery}
        onSearch={handleSearch}
        isLoading={isSearching}
      />

      {/* =========================
          EMPTY STATE
      ========================== */}
      {!hasFiles &&
        !indexStatus?.is_indexing &&
        !isLoadingStatus && (
          <EmptyState
            onAddFolder={() => setIsFolderManagerOpen(true)}
            onUseSampleFolder={handleUseDemo}
          />
        )}

      {/* =========================
          SEARCH RESULTS
      ========================== */}
      {searchResults && (
        <div className="mt-8">
          <SearchResults
            response={searchResults}
            onShowContext={(item) => setSelectedContext(item)}
          />
        </div>
      )}

      {/* =========================
          RECENT SEARCHES
      ========================== */}
      {searchHistory.length > 0 &&
        !searchResults &&
        hasFiles && (
          <div className="mt-8 pt-6 border-t border-neutral-200">

            <div className="flex items-center justify-between mb-3 text-xs text-neutral-500">

              <span className="font-semibold text-neutral-800">
                Recent Searches
              </span>

              <button
                type="button"
                onClick={handleClearHistory}
                className="flex items-center gap-1 text-neutral-400 hover:text-neutral-700 transition-colors"
                title="Clear search history"
              >
                <Trash2 className="w-3 h-3" />
                Clear
              </button>

            </div>

            <div className="space-y-1.5">

              {searchHistory.slice(0, 5).map((item) => (
                <button
                  type="button"
                  key={item.id}
                  onClick={() => {
                    setQuery(item.query);
                    handleSearch(item.query);
                  }}
                  disabled={isSearching}
                  className="w-full flex items-center justify-between px-3 py-2 text-xs text-left bg-white hover:bg-neutral-50 border border-neutral-200 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >

                  <div className="flex items-center gap-2 text-neutral-700">

                    <Clock className="w-3.5 h-3.5 text-neutral-400 shrink-0" />

                    <span className="font-mono">
                      {item.query}
                    </span>

                  </div>

                  <span className="text-[11px] text-neutral-400 font-mono">
                    {item.result_count}{' '}
                    {item.result_count === 1
                      ? 'match'
                      : 'matches'}
                  </span>

                </button>
              ))}

            </div>
          </div>
        )}

      {/* =========================
          FOLDER MANAGER
      ========================== */}
      <FolderSelector
        folders={indexStatus?.indexed_folders || []}
        onAddFolder={handleAddFolder}
        onRemoveFolder={handleRemoveFolder}
        isOpen={isFolderManagerOpen}
        onClose={() => setIsFolderManagerOpen(false)}
      />

      {/* =========================
          CONTEXT MODAL
      ========================== */}
      <ContextModal
        result={selectedContext}
        onClose={() => setSelectedContext(null)}
      />

    </div>
  );
};