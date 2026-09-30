import React from 'react';
import { HardDrive, Settings as SettingsIcon, Search, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  activeTab: 'search' | 'settings';
  setActiveTab: (tab: 'search' | 'settings') => void;
  hardwareDevice?: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  hardwareDevice = 'Apple Silicon M1 / Local CPU',
}) => {
  return (
    <header className="border-b border-neutral-200 bg-white sticky top-0 z-20">
      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-neutral-800" />
            <h1 className="text-base font-semibold tracking-tight text-neutral-900">
              MY PC REMEMBERS
            </h1>
          </div>
          <div className="flex items-center gap-2 text-xs text-neutral-500 mt-0.5">
            <span>Private local AI memory</span>
            <span aria-hidden="true">·</span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-neutral-600" />
              100% on-device
            </span>
            <span aria-hidden="true">·</span>
            <span>{hardwareDevice}</span>
          </div>
        </div>

        <nav className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab('search')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
              activeTab === 'search'
                ? 'bg-neutral-900 text-white border-neutral-900'
                : 'bg-white text-neutral-600 border-neutral-200 hover:text-neutral-900 hover:border-neutral-300'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            Search
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
              activeTab === 'settings'
                ? 'bg-neutral-900 text-white border-neutral-900'
                : 'bg-white text-neutral-600 border-neutral-200 hover:text-neutral-900 hover:border-neutral-300'
            }`}
          >
            <SettingsIcon className="w-3.5 h-3.5" />
            Settings
          </button>
        </nav>
      </div>
    </header>
  );
};
