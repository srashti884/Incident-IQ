import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  AlertOctagon, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Flame,
  ArrowRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  Cell 
} from 'recharts';
import { api } from '../services/api';
import WhatChangedWidget from '../components/WhatChangedWidget';

export default function DashboardPage({ onSelectIncident }) {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [whatChangedData, setWhatChangedData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dash, changed] = await Promise.all([
        api.getDashboard(),
        api.getWhatChanged()
      ]);
      setDashboardData(dash);
      setWhatChangedData(changed);
    } catch (err) {
      setError('Unable to load local warehouse analytics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKpiClick = (filterKey, filterVal) => {
    navigate(`/explorer?${filterKey}=${encodeURIComponent(filterVal)}`);
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center text-slate-500 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span>Loading local warehouse metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded text-sm">
          {error}
        </div>
      </div>
    );
  }

  const { kpis, incidents_by_severity, incidents_by_application, incidents_by_status, trend_over_time, sla_trend } = dashboardData;

  const SEV_COLORS = {
    'Critical': '#E11D48',
    'High': '#D97706',
    'Medium': '#2563EB',
    'Low': '#64748B'
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        
        {/* Total Incidents */}
        <div 
          onClick={() => navigate('/explorer')}
          className="bg-white border border-slate-200 rounded p-4 shadow-xs hover:border-slate-300 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Volume</span>
            <Layers className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tabular-nums">
            {kpis.total_incidents.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">All Recorded Tickets</div>
        </div>

        {/* Open Incidents */}
        <div 
          onClick={() => handleKpiClick('status', 'Open')}
          className="bg-white border border-slate-200 rounded p-4 shadow-xs hover:border-amber-300 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider">Open / Active</span>
            <AlertTriangle className="w-4 h-4 text-amber-500 group-hover:text-amber-600 transition" />
          </div>
          <div className="text-2xl font-bold text-amber-600 tabular-nums">
            {kpis.open_incidents}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Requiring Mitigation</div>
        </div>

        {/* Critical Incidents */}
        <div 
          onClick={() => handleKpiClick('severity', 'Critical')}
          className="bg-white border border-slate-200 rounded p-4 shadow-xs hover:border-rose-300 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider">Critical (P1)</span>
            <Flame className="w-4 h-4 text-rose-500 group-hover:text-rose-600 transition" />
          </div>
          <div className="text-2xl font-bold text-rose-600 tabular-nums">
            {kpis.critical_incidents}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Highest Priority</div>
        </div>

        {/* Resolved Incidents */}
        <div 
          onClick={() => handleKpiClick('status', 'Resolved')}
          className="bg-white border border-slate-200 rounded p-4 shadow-xs hover:border-emerald-300 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider">Resolved</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500 group-hover:text-emerald-600 transition" />
          </div>
          <div className="text-2xl font-bold text-emerald-600 tabular-nums">
            {kpis.resolved_incidents.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Normal Operations</div>
        </div>

        {/* SLA Breaches */}
        <div 
          onClick={() => handleKpiClick('sla_breached', '1')}
          className="bg-white border border-slate-200 rounded p-4 shadow-xs hover:border-rose-300 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider">SLA Breaches</span>
            <AlertOctagon className="w-4 h-4 text-rose-500 group-hover:text-rose-600 transition" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tabular-nums">
            {kpis.sla_breaches}
          </div>
          <div className="text-[11px] text-rose-600 font-semibold mt-1">
            {kpis.sla_breach_rate}% Breach Rate
          </div>
        </div>

        {/* Average Resolution Time (MTTR) */}
        <div className="bg-white border border-slate-200 rounded p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider">MTTR (Avg)</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tabular-nums">
            {kpis.avg_resolution_time} <span className="text-sm font-normal text-slate-500">m</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Mean Time To Resolve</div>
        </div>

      </div>

      {/* Differentiating Feature: What Changed Since Yesterday */}
      <WhatChangedWidget data={whatChangedData} />

      {/* Primary Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Incident Trend Over Time */}
        <div className="bg-white border border-slate-200 rounded p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Incident Trend Over Time (Last 30 Days)
              </h2>
              <div className="text-[11px] text-slate-400">Daily incident volume & critical alerts</div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend_over_time} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="date_day" 
                  tickFormatter={(val) => val.slice(5)} 
                  tick={{ fontSize: 10, fill: '#64748b' }} 
                />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="total" name="Total Incidents" stroke="#2563EB" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="critical" name="Critical (P1)" stroke="#E11D48" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Incident-Generating Applications */}
        <div className="bg-white border border-slate-200 rounded p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Incidents by Application Tier
              </h2>
              <div className="text-[11px] text-slate-400">Ranked by overall operational volume</div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={incidents_by_application} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis 
                  type="category" 
                  dataKey="application" 
                  tick={{ fontSize: 9, fill: '#334155' }} 
                  width={110}
                  tickFormatter={(val) => val.length > 16 ? val.slice(0, 16) + '...' : val}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="incident_count" name="Total Incidents" fill="#2563EB" radius={[0, 2, 2, 0]} />
                <Bar dataKey="critical_count" name="Critical (P1)" fill="#E11D48" radius={[0, 2, 2, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Incidents by Severity */}
        <div className="bg-white border border-slate-200 rounded p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Incidents by Severity
              </h2>
              <div className="text-[11px] text-slate-400">Distribution across operational priority tiers</div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={incidents_by_severity} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="severity" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }}
                />
                <Bar dataKey="count" name="Count" radius={[2, 2, 0, 0]}>
                  {incidents_by_severity.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEV_COLORS[entry.severity] || '#64748b'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SLA Breaches Trend */}
        <div className="bg-white border border-slate-200 rounded p-5 shadow-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                SLA Breaches vs Average MTTR
              </h2>
              <div className="text-[11px] text-slate-400">Correlation of breach frequency and resolution duration</div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sla_trend} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="date_day" 
                  tickFormatter={(val) => val.slice(5)} 
                  tick={{ fontSize: 10, fill: '#64748b' }} 
                />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="breaches" name="SLA Breaches" stroke="#E11D48" strokeWidth={2} />
                <Line type="monotone" dataKey="avg_resolution" name="Avg Resolution (min)" stroke="#64748B" strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
}
