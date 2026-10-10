import React, { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';
import { TrendingUp, Clock, AlertOctagon, Layers } from 'lucide-react';
import { api } from '../services/api';

export default function TrendsPage() {
  const [trendData, setTrendData] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.invokeMcpTool('get_trend_metrics', { interval: 'daily', days: 45 }),
      api.getDashboard()
    ]).then(([mcpRes, dash]) => {
      if (mcpRes.success) {
        setTrendData(mcpRes.data.points || []);
      }
      setDashboardData(dash);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 text-xs">
        Loading historical trend analytics from local warehouse...
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Page Header Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            <span>Operational Trends & Trajectory Analysis</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Historical incident volume, MTTR variations, and SLA breach rate shifts computed from local warehouse data.
          </p>
        </div>
        <div className="text-right text-xs text-slate-400 font-mono">
          Horizon: Trailing 45 Days
        </div>
      </div>

      {/* Chart 1: Daily Incident Volume & Critical Alerts Area Chart */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
        <div className="pb-3 mb-3 border-b border-slate-100 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Daily Incident Ingestion & Critical Alerts (Trailing 45 Days)
          </span>
          <span className="text-[11px] text-slate-400">Area breakdown</span>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorInc" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorCrit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#E11D48" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#E11D48" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date_interval" tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => v.slice(5)} />
              <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }} />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Area type="monotone" dataKey="incident_count" name="Total Daily Incidents" stroke="#2563EB" fillOpacity={1} fill="url(#colorInc)" />
              <Area type="monotone" dataKey="critical_count" name="Critical Incidents (P1)" stroke="#E11D48" fillOpacity={1} fill="url(#colorCrit)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Grid: SLA Breaches Trend & Application Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* SLA Breaches Over Time */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="pb-3 mb-3 border-b border-slate-100 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
              <AlertOctagon className="w-4 h-4 text-rose-500" />
              <span>SLA Breaches Progression</span>
            </span>
            <span className="text-[11px] text-slate-400">Daily breached volume</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date_interval" tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }} />
                <Bar dataKey="sla_breaches" name="SLA Breaches" fill="#E11D48" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Incident Applications Breakdown */}
        {dashboardData && (
          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
            <div className="pb-3 mb-3 border-b border-slate-100 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                <Layers className="w-4 h-4 text-slate-500" />
                <span>Application Load Distribution</span>
              </span>
              <span className="text-[11px] text-slate-400">Cumulative historical share</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dashboardData.incidents_by_application} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis type="category" dataKey="application" tick={{ fontSize: 9, fill: '#334155' }} width={110} tickFormatter={(v) => v.slice(0, 16)} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }} />
                  <Bar dataKey="incident_count" name="Incidents" fill="#0284C7" radius={[0, 2, 2, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
