import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Home } from './pages/Home';
import { SettingsPage } from './pages/Settings';
import { IndexStatusResponse, HardwareInfo } from './types';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<'search' | 'settings'>('search');
  const [indexStatus, setIndexStatus] = useState<IndexStatusResponse | null>(null);
  const [hardware, setHardware] = useState<HardwareInfo | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [s, h] = await Promise.allSettled([
        api.getIndexStatus(),
        api.getHardwareInfo(),
      ]);
      if (s.status === 'fulfilled') setIndexStatus(s.value);
      if (h.status === 'fulfilled') setHardware(h.value);
    } catch (err) {
      console.error('Initial data load error:', err);
    }
  };

  const hardwareDevice = hardware?.hardware_profile?.hardware_target || 'Apple Silicon M1 / Local CPU';

  return (
    <div className="min-h-screen bg-neutral-50/50 text-neutral-900 font-sans flex flex-col">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hardwareDevice={hardwareDevice}
      />

      <main className="flex-1">
        {activeTab === 'search' ? (
          <Home />
        ) : (
          <SettingsPage
            indexStatus={indexStatus}
            onRefreshStatus={loadInitialData}
          />
        )}
      </main>

      <footer className="border-t border-neutral-200 bg-white py-4 mt-auto">
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-neutral-500">
          <div>
            <span className="font-semibold text-neutral-800">MY PC REMEMBERS</span>
            <span aria-hidden="true" className="mx-1.5">·</span>
            <span>Private Local AI Memory</span>
          </div>
          <div className="flex items-center gap-2">
            <span>Prepared for Snapdragon AI Lab Challenge</span>
            <span aria-hidden="true">·</span>
            <span>Zero Cloud Dependency</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
