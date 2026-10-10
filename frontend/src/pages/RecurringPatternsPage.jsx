import React, { useState, useEffect } from 'react';
import { Repeat, ArrowUpRight, ArrowDownRight, Minus, AlertTriangle, Layers, ChevronRight, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function RecurringPatternsPage({ onSelectIncident }) {
  const [patterns, setPatterns] = useState([]);
  const [selectedPattern, setSelectedPattern] = useState(null);
  const [patternIncidents, setPatternIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingIncidents, setLoadingIncidents] = useState(false);

  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    setLoading(true);
    try {
      const res = await api.getPatterns();
      const loadedPatterns = res.patterns || [];
      setPatterns(loadedPatterns);
      if (loadedPatterns.length > 0) {
        selectPattern(loadedPatterns[0]);
      }
    } catch (err) {
      console.error('Failed to load recurring patterns:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectPattern = async (pat) => {
    setSelectedPattern(pat);
    setLoadingIncidents(true);
    try {
      const res = await api.getPatternIncidents(pat.pattern_id);
      setPatternIncidents(res.incidents || []);
    } catch (err) {
      console.error('Failed to load pattern incidents:', err);
    } finally {
      setLoadingIncidents(false);
    }
  };

  const renderTrendBadge = (trend) => {
    if (trend === 'Increasing') {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          <ArrowUpRight className="w-3 h-3" />
          <span>Increasing</span>
        </span>
      );
    } else if (trend === 'Decreasing') {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <ArrowDownRight className="w-3 h-3" />
          <span>Decreasing</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
        <Minus className="w-3 h-3" />
        <span>Stable</span>
      </span>
    );
  };

  const renderRiskBadge = (riskLevel) => {
    switch (riskLevel) {
      case 'High Recurrence Risk':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'Medium Recurrence Risk':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Low Recurrence Risk':
        return 'bg-slate-100 text-slate-700 border-slate-200';
      case 'Insufficient Historical Data':
      default:
        return 'bg-slate-50 text-slate-500 border-slate-200';
    }
  };

  // Robust calculation for Recurrence Risk Estimate using local incident data
  const getRecurrenceRisk = (pat) => {
    if (!pat) {
      return {
        riskLevel: 'Insufficient Historical Data',
        explanation: 'No recurring pattern data available.'
      };
    }

    // If backend provided a valid risk_level, use it
    if (pat.prediction && pat.prediction.risk_level && pat.prediction.risk_level !== 'N/A') {
      return {
        riskLevel: pat.prediction.risk_level,
        explanation: pat.prediction.explanation || 'Calculated based on local historical recurrence data.'
      };
    }

    // Factual local calculation based on occurrence count, recency, and trend
    const occurrences = Number(pat.occurrences) || 0;
    const trend = pat.trend || 'Stable';

    if (occurrences < 5) {
      return {
        riskLevel: 'Insufficient Historical Data',
        explanation: `Insufficient historical occurrences (${occurrences} events) for statistically reliable recurrence estimation.`
      };
    }

    let daysSinceLast = null;
    if (pat.last_seen) {
      const lastDt = new Date(pat.last_seen.replace(' ', 'T'));
      const refDt = new Date('2026-09-22T12:00:00');
      if (!isNaN(lastDt.getTime())) {
        daysSinceLast = Math.max(0, Math.floor((refDt - lastDt) / (1000 * 60 * 60 * 24)));
      }
    }

    if (trend === 'Increasing') {
      return {
        riskLevel: 'High Recurrence Risk',
        explanation: `Elevated recurrence likelihood based on high historical frequency (${occurrences} occurrences) and active increasing trend${daysSinceLast !== null ? ` (last seen ${daysSinceLast}d ago)` : ''}.`
      };
    } else if (trend === 'Stable' || (daysSinceLast !== null && daysSinceLast <= 14)) {
      return {
        riskLevel: 'Medium Recurrence Risk',
        explanation: `Moderate recurrence likelihood with consistent historical baseline (${occurrences} occurrences)${daysSinceLast !== null ? ` and recent detection ${daysSinceLast}d ago` : ''}.`
      };
    } else {
      return {
        riskLevel: 'Low Recurrence Risk',
        explanation: `Low recurrence likelihood with ${trend.toLowerCase()} trajectory and reduced recent activity.`
      };
    }
  };

  // Robust Early Warning detection
  const getEarlyWarning = (pat) => {
    if (!pat) return { triggered: false, message: null, reason: null };
    if (pat.early_warning && typeof pat.early_warning.triggered === 'boolean') {
      return pat.early_warning;
    }
    if (pat.trend === 'Increasing') {
      return {
        triggered: true,
        message: 'Recurring pattern increasing — investigation recommended.',
        reason: 'Recent occurrences are higher than historical baseline.'
      };
    }
    return { triggered: false, message: null, reason: null };
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-2">
            <Repeat className="w-4 h-4 text-blue-600" />
            <span>Recurring Incident Fingerprints & Pattern Recognition</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Deterministic TF-IDF similarity clustering identifies chronic system failure vectors, future recurrence risk, and escalation early warnings.
          </p>
        </div>
        <div className="text-right text-xs font-mono text-slate-400">
          {patterns.length} High-Confidence Patterns Identified
        </div>
      </div>

      {/* Main Grid: Patterns List & Incident Drill-down */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Patterns Table */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Active Incident Fingerprints
            </span>
            <span className="text-[11px] text-slate-400">Select to inspect matched instances</span>
          </div>

          <div className="divide-y divide-slate-200">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading patterns...</div>
            ) : (
              patterns.map((pat) => {
                const isSelected = selectedPattern?.pattern_id === pat.pattern_id;
                const risk = getRecurrenceRisk(pat);
                const warning = getEarlyWarning(pat);

                return (
                  <div
                    key={pat.pattern_id}
                    onClick={() => selectPattern(pat)}
                    className={`p-4 transition cursor-pointer ${
                      isSelected ? 'bg-blue-50/70 border-l-4 border-l-blue-600' : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-slate-900">{pat.pattern_id}</span>
                        <span className="text-xs font-semibold text-blue-700 bg-blue-100/60 px-2 py-0.5 rounded">
                          {pat.fingerprint}
                        </span>
                      </div>
                      {renderTrendBadge(pat.trend)}
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-slate-600 mt-2 bg-white/70 p-2 rounded border border-slate-200/60">
                      <div>
                        <span className="text-[11px] text-slate-400 block">Application</span>
                        <span className="font-medium text-slate-800">{pat.application}</span>
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400 block">Occurrences</span>
                        <span className="font-bold text-slate-900">{pat.occurrences} instances</span>
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400 block">Avg MTTR</span>
                        <span className="font-mono text-slate-800">{pat.avg_resolution_minutes} min</span>
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-400 block">Last Detected</span>
                        <span className="font-mono text-slate-700">{pat.last_seen ? pat.last_seen.slice(5, 10) : '—'}</span>
                      </div>
                    </div>

                    <div className="mt-2 text-xs text-slate-600 flex items-start space-x-1">
                      <span className="text-slate-400 font-medium shrink-0">Hypothesized Cause:</span>
                      <span className="text-slate-700 italic">{pat.possible_root_cause}</span>
                    </div>

                    {/* FEATURE 1: Future Incident Prediction / Recurrence Risk */}
                    <div className="mt-2.5 pt-2 border-t border-slate-100 text-xs">
                      <div className="flex items-center space-x-2">
                        <span className="text-slate-500 font-medium">Recurrence Risk (Estimate):</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${renderRiskBadge(risk.riskLevel)}`}>
                          {risk.riskLevel}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-1 leading-snug">
                        {risk.explanation}
                      </div>
                    </div>

                    {/* FEATURE 2: Early Warning Indicator (Active only when pattern is escalating) */}
                    {warning.triggered && (
                      <div className="mt-2.5 p-2.5 bg-rose-50 border border-rose-200 rounded text-xs text-rose-900 flex items-start space-x-2">
                        <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                        <div>
                          <div className="font-bold text-rose-800">
                            Early Warning: {warning.message}
                          </div>
                          <div className="text-[11px] text-rose-700 mt-0.5 leading-snug">
                            Reason: {warning.reason}
                          </div>
                        </div>
                      </div>
                    )}

                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Matched Incidents Panel */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden flex flex-col h-full">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Matched Incidents: {selectedPattern ? selectedPattern.pattern_id : 'None'}
            </span>
            <div className="text-[11px] text-slate-400 mt-0.5">
              {patternIncidents.length} verified incident tickets sharing fingerprint signature
            </div>
          </div>

          {/* Selected Pattern Prediction & Early Warning Summary */}
          {selectedPattern && (() => {
            const selectedRisk = getRecurrenceRisk(selectedPattern);
            const selectedWarning = getEarlyWarning(selectedPattern);

            return (
              <div className="p-3.5 bg-slate-50/80 border-b border-slate-200 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600 font-semibold">Recurrence Risk Estimate:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${renderRiskBadge(selectedRisk.riskLevel)}`}>
                    {selectedRisk.riskLevel}
                  </span>
                </div>
                <div className="text-[11px] text-slate-600 leading-snug">
                  {selectedRisk.explanation}
                </div>
                {selectedWarning.triggered && (
                  <div className="p-2 bg-rose-50 border border-rose-200 rounded text-rose-900 text-[11px] flex items-center space-x-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    <span className="font-semibold">{selectedWarning.message}</span>
                  </div>
                )}
              </div>
            );
          })()}

          <div className="flex-1 overflow-y-auto p-3 space-y-2 max-h-[580px]">
            {loadingIncidents ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading instances...</div>
            ) : patternIncidents.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No instances loaded.</div>
            ) : (
              patternIncidents.map((inc) => (
                <div
                  key={inc.incident_id}
                  onClick={() => onSelectIncident(inc.incident_id)}
                  className="p-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded text-xs transition cursor-pointer group"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-blue-600 group-hover:underline">
                      {inc.incident_id}
                    </span>
                    <span className="text-[11px] font-mono text-slate-500">{inc.created_at.slice(0, 16)}</span>
                  </div>
                  <div className="font-medium text-slate-800 leading-snug">{inc.title}</div>
                  <div className="flex items-center space-x-2 mt-2 text-[11px] text-slate-500">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      inc.severity === 'Critical' ? 'bg-rose-100 text-rose-800' : 'bg-slate-200 text-slate-700'
                    }`}>
                      {inc.severity}
                    </span>
                    <span>•</span>
                    <span>{inc.service}</span>
                    <span>•</span>
                    <span>{inc.resolution_time_minutes ? `${inc.resolution_time_minutes}m` : 'In Progress'}</span>
                    {inc.sla_breached === 1 && (
                      <span className="text-rose-600 font-semibold">• SLA Breached</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
