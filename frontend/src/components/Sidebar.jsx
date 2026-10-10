import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  Layers, 
  TrendingUp, 
  Repeat, 
  Activity, 
  FileText, 
  Database
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analytics', label: 'Natural Language Analytics', icon: Search },
  { path: '/explorer', label: 'Incident Explorer', icon: Layers },
  { path: '/trends', label: 'Trends & Analysis', icon: TrendingUp },
  { path: '/patterns', label: 'Recurring Patterns', icon: Repeat },
  { path: '/impact-matrix', label: 'Impact vs Severity', icon: Activity },
  { path: '/reports', label: 'Reports Hub', icon: FileText },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 min-h-screen border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 bg-blue-600 rounded flex items-center justify-center font-bold text-white text-sm tracking-wider">
            IQ
          </div>
          <div>
            <div className="text-sm font-bold text-white tracking-wide">IncidentIQ</div>
            <div className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">Operations Platform</div>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Core Modules
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-xs'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Offline Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950 text-[11px] text-slate-400">
        <div className="flex items-center justify-between">
          <span>Local Engine</span>
          <span className="text-emerald-400 font-mono text-[10px] font-semibold">100% OFFLINE</span>
        </div>
        <div className="text-[10px] text-slate-500 mt-1">
          Zero Cloud Dependencies
        </div>
      </div>
    </aside>
  );
}
