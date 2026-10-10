import React from 'react';
import { X, Clock, AlertTriangle, CheckCircle, ShieldAlert, FileText, ArrowRight, User } from 'lucide-react';

export default function IncidentStoryDrawer({ storyData, isOpen, onClose }) {
  if (!isOpen || !storyData) return null;

  const { incident, timeline, related_incidents, impact_analysis } = storyData;

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'Critical':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'High':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Medium':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Open':
        return 'bg-rose-100 text-rose-800';
      case 'In Progress':
        return 'bg-amber-100 text-amber-800';
      case 'Resolved':
        return 'bg-emerald-100 text-emerald-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col border-l border-slate-200">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-start justify-between bg-slate-50">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="font-mono text-sm font-bold text-slate-900">{incident.incident_id}</span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getSeverityBadge(incident.severity)}`}>
                {incident.severity}
              </span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${getStatusBadge(incident.status)}`}>
                {incident.status}
              </span>
              {incident.sla_breached === 1 && (
                <span className="bg-rose-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded">
                  SLA BREACHED
                </span>
              )}
            </div>
            <h2 className="text-base font-semibold text-slate-900 leading-snug">{incident.title}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-4 bg-slate-50 border border-slate-200 rounded p-4 text-xs">
            <div>
              <span className="text-slate-500 font-medium">Application:</span>
              <div className="font-semibold text-slate-900 mt-0.5">{incident.application}</div>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Service Component:</span>
              <div className="font-semibold text-slate-900 mt-0.5">{incident.service}</div>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Assignee:</span>
              <div className="font-semibold text-slate-900 mt-0.5 flex items-center space-x-1">
                <User className="w-3.5 h-3.5 text-slate-400" />
                <span>{incident.assignee}</span>
              </div>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Reporter:</span>
              <div className="font-semibold text-slate-900 mt-0.5">{incident.reporter}</div>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Created Timestamp:</span>
              <div className="font-mono text-slate-700 mt-0.5">{incident.created_at}</div>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Resolution Duration:</span>
              <div className="font-mono text-slate-700 mt-0.5">
                {incident.resolution_time_minutes ? `${incident.resolution_time_minutes} mins (Target: ${incident.sla_target_minutes} mins)` : 'In progress'}
              </div>
            </div>
          </div>

          {/* Incident Lifecycle Timeline */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center space-x-1.5">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>Incident Lifecycle Timeline</span>
            </h3>
            
            <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {timeline.map((step, idx) => (
                <div key={idx} className="relative group">
                  <div className="absolute -left-6 top-1 w-4 h-4 rounded-full border-2 border-white bg-blue-600 ring-2 ring-blue-100 flex items-center justify-center" />
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-slate-900">{step.stage}</span>
                      <span className="text-[11px] font-mono text-slate-400">{step.timestamp}</span>
                      <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-medium">{step.actor}</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Root Cause & Operational Impact */}
          <div className="border-t border-slate-200 pt-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>Root Cause & Calculated Impact</span>
            </h3>

            <div className="bg-amber-50/50 border border-amber-200 rounded p-3.5 mb-3 text-xs">
              <div className="font-semibold text-amber-900">
                Identified Category: {incident.root_cause_category}
              </div>
              <div className="text-amber-800 mt-1">
                {incident.root_cause_summary}
              </div>
            </div>

            <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded p-3 text-xs">
              <div>
                <span className="text-slate-500">Calculated Impact Score:</span>
                <div className="font-bold text-slate-900 text-lg">{incident.impact_score} / 100</div>
              </div>
              <div className="text-right text-[11px] text-slate-500">
                Formula: Severity (40%) + SLA Penalty (20%) + Tier Weight (20%) + MTTR (20%)
              </div>
            </div>
          </div>

          {/* Related Incidents */}
          {related_incidents && related_incidents.length > 0 && (
            <div className="border-t border-slate-200 pt-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center space-x-1.5">
                <FileText className="w-4 h-4 text-slate-400" />
                <span>Correlated & Prior Related Incidents</span>
              </h3>

              <div className="space-y-2">
                {related_incidents.map((rel) => (
                  <div key={rel.incident_id} className="p-2.5 bg-slate-50 border border-slate-200 rounded text-xs hover:bg-slate-100 transition">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-slate-800">{rel.incident_id}</span>
                      <span className="text-[11px] text-slate-500 font-mono">{rel.created_at}</span>
                    </div>
                    <div className="text-slate-700 font-medium">{rel.title}</div>
                    <div className="flex items-center space-x-2 mt-1.5 text-[11px] text-slate-500">
                      <span>Severity: {rel.severity}</span>
                      <span>•</span>
                      <span>Category: {rel.root_cause_category}</span>
                      <span>•</span>
                      <span>Duration: {rel.resolution_time_minutes ? `${rel.resolution_time_minutes}m` : 'N/A'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-100 transition cursor-pointer"
          >
            Close Drill-Down
          </button>
        </div>

      </div>
    </div>
  );
}
