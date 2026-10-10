import React from 'react';
import { Database, RefreshCw, Server } from 'lucide-react';

export default function Header({ title, subtitle, warehouseStats, lastRefreshed, onRefresh, isRefreshing }) {
  const isConnected = warehouseStats?.status === 'CONNECTED';
  const totalIncidents = warehouseStats?.total_incidents || 0;

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3.5 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center space-x-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">IncidentIQ Enterprise</span>
            <span className="text-slate-300">/</span>
            <span className="text-xs font-medium text-slate-600">{title}</span>
          </div>
          <h1 className="text-lg font-bold text-slate-900 tracking-tight">{title}</h1>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Local Warehouse Connection Badge */}
        <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded px-3 py-1.5 text-xs text-slate-600">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
          <span className="font-semibold text-slate-700">LOCAL WAREHOUSE</span>
          <span className="text-slate-400">●</span>
          <span>{isConnected ? `CONNECTED (${totalIncidents.toLocaleString()} records)` : 'DISCONNECTED'}</span>
        </div>

        {/* Timestamp */}
        <div className="text-xs text-slate-500 hidden sm:block">
          Last refreshed: <span className="font-mono font-medium text-slate-700">{lastRefreshed || 'Just now'}</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 active:bg-slate-100 disabled:opacity-50 transition shadow-xs cursor-pointer"
          title="Refresh local warehouse cache and metrics"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-600 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>
    </header>
  );
}
