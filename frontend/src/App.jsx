import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import IncidentStoryDrawer from './components/IncidentStoryDrawer';

import DashboardPage from './pages/DashboardPage';
import NLAnalyticsPage from './pages/NLAnalyticsPage';
import IncidentExplorerPage from './pages/IncidentExplorerPage';
import TrendsPage from './pages/TrendsPage';
import RecurringPatternsPage from './pages/RecurringPatternsPage';
import ImpactMatrixPage from './pages/ImpactMatrixPage';
import ReportsPage from './pages/ReportsPage';
import SystemWarehousePage from './pages/SystemWarehousePage';

import { api } from './services/api';

const PAGE_TITLES = {
  '/': 'Operational Dashboard',
  '/analytics': 'Natural Language Analytics & Reporting',
  '/explorer': 'Incident Explorer & Triage',
  '/trends': 'Historical Trends & Trajectory',
  '/patterns': 'Recurring Incident Fingerprints',
  '/impact-matrix': 'Severity vs Operational Impact Matrix',
  '/reports': 'Executive Reports & Compliance Audit',
  '/system': 'Local Warehouse Health & MCP Tools',
};

function MainLayout() {
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] || 'IncidentIQ Platform';

  const [warehouseStats, setWarehouseStats] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Incident Story Drilldown state
  const [selectedIncidentStory, setSelectedIncidentStory] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const fetchStats = async () => {
    setIsRefreshing(true);
    try {
      const stats = await api.getSystemStatus();
      setWarehouseStats(stats);
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to fetch warehouse stats:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSelectIncident = async (incidentId) => {
    try {
      const story = await api.getIncidentStory(incidentId);
      setSelectedIncidentStory(story);
      setIsDrawerOpen(true);
    } catch (err) {
      alert(`Could not load story for ${incidentId}: ${err.message}`);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header 
          title={title} 
          warehouseStats={warehouseStats} 
          lastRefreshed={lastRefreshed} 
          onRefresh={fetchStats}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<DashboardPage onSelectIncident={handleSelectIncident} />} />
            <Route path="/analytics" element={<NLAnalyticsPage onSelectIncident={handleSelectIncident} />} />
            <Route path="/explorer" element={<IncidentExplorerPage onSelectIncident={handleSelectIncident} />} />
            <Route path="/trends" element={<TrendsPage />} />
            <Route path="/patterns" element={<RecurringPatternsPage onSelectIncident={handleSelectIncident} />} />
            <Route path="/impact-matrix" element={<ImpactMatrixPage onSelectIncident={handleSelectIncident} />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/system" element={<SystemWarehousePage warehouseStats={warehouseStats} />} />
          </Routes>
        </main>
      </div>

      {/* Incident Story Drill-down Drawer */}
      <IncidentStoryDrawer 
        storyData={selectedIncidentStory} 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
      />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <MainLayout />
    </BrowserRouter>
  );
}
