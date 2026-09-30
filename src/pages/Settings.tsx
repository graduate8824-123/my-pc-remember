import React, { useState } from 'react';
import { SettingsPanel } from '../components/SettingsPanel';
import { FolderSelector } from '../components/FolderSelector';
import { IndexStatusResponse } from '../types';
import { api } from '../services/api';

interface SettingsPageProps {
  indexStatus: IndexStatusResponse | null;
  onRefreshStatus: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  indexStatus,
  onRefreshStatus,
}) => {
  const [isFolderManagerOpen, setIsFolderManagerOpen] = useState(false);

  const handleAddFolder = async (path: string) => {
    await api.addFolder(path);
    onRefreshStatus();
  };

  const handleRemoveFolder = async (id: number) => {
    await api.removeFolder(id);
    onRefreshStatus();
  };

  const handleRebuild = async () => {
    if (confirm('Rebuilding will clear the vector index and re-index all user folders. Proceed?')) {
      await api.rebuildIndex();
      onRefreshStatus();
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <SettingsPanel
        folders={indexStatus?.indexed_folders || []}
        onOpenFolderManager={() => setIsFolderManagerOpen(true)}
        onRebuildIndex={handleRebuild}
      />

      <FolderSelector
        folders={indexStatus?.indexed_folders || []}
        onAddFolder={handleAddFolder}
        onRemoveFolder={handleRemoveFolder}
        isOpen={isFolderManagerOpen}
        onClose={() => setIsFolderManagerOpen(false)}
      />
    </div>
  );
};
