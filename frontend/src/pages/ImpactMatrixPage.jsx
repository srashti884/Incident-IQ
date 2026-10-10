import React, { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  ZAxis, 
  CartesianGrid, 
  Tooltip, 
  Cell 
} from 'recharts';
import { Activity, Info, ShieldAlert, CheckCircle } from 'lucide-react';
import { api } from '../services/api';

export default function ImpactMatrixPage({ onSelectIncident }) {
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getImpactMatrix(200).then(data => setMatrixData(data)).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-xs text-slate-400">
        Computing Severity vs Operational Impact matrix from local warehouse...
      </div>
    );
  }

  const { points, formula, total_analyzed } = matrixData;

  const SEV_NAMES = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Critical'
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 text-white text-xs p-3 rounded shadow-lg border border-slate-700 max-w-xs">
          <div className="flex items-center justify-between mb-1">
            <span className="font-mono font-bold text-blue-400">{data.incident_id}</span>
            <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded">{data.severity}</span>
          </div>
          <div className="font-medium text-slate-200 mb-2">{data.title}</div>
          <div className="border-t border-slate-800 pt-1.5 space-y-0.5 text-[11px] text-slate-300">
            <div>Application: <span className="text-white font-medium">{data.application}</span></div>
            <div>Calculated Impact Score: <span className="text-amber-400 font-bold">{data.impact_score}/100</span></div>
            <div>SLA Breached: <span className={data.sla_breached ? "text-rose-400 font-bold" : "text-emerald-400 font-medium"}>{data.sla_breached ? "Yes" : "No"}</span></div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-2">
            <Activity className="w-4 h-4 text-blue-600" />
            <span>Severity Level vs Calculated Operational Impact</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Correlates assigned ticket severity with multi-factor calculated business impact score.
          </p>
        </div>
        <div className="text-right text-xs font-mono text-slate-400">
          {total_analyzed} Incident Data Points Plotted
        </div>
      </div>

      {/* Formula Explanation Callout */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-lg p-4 text-xs text-slate-700 flex items-start space-x-2.5">
        <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-blue-900 block mb-0.5">Calculated Impact Score Methodology:</span>
          <span>{formula}</span>
        </div>
      </div>

      {/* Scatter Visualization */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
        <div className="pb-3 mb-3 border-b border-slate-100 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Operational Impact Scatter Distribution
          </span>
          <span className="text-[11px] text-slate-400">Hover point to inspect incident details</span>
        </div>
        
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                type="number" 
                dataKey="severity_level" 
                name="Severity Level" 
                domain={[0.5, 4.5]} 
                ticks={[1, 2, 3, 4]}
                tickFormatter={(v) => SEV_NAMES[v] || ''}
                tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }}
              />
              <YAxis 
                type="number" 
                dataKey="impact_score" 
                name="Calculated Impact Score" 
                domain={[0, 100]} 
                tick={{ fontSize: 10, fill: '#64748b' }}
                label={{ value: 'Calculated Operational Impact Score (1-100)', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#64748b' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Scatter 
                name="Incidents" 
                data={points} 
                onClick={(e) => e && onSelectIncident && onSelectIncident(e.incident_id)}
                cursor="pointer"
              >
                {points.map((entry, index) => {
                  const color = entry.severity === 'Critical' ? '#E11D48' :
                                entry.severity === 'High' ? '#D97706' :
                                entry.severity === 'Medium' ? '#2563EB' : '#64748B';
                  return <Cell key={`cell-${index}`} fill={color} fillOpacity={0.7} />;
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
