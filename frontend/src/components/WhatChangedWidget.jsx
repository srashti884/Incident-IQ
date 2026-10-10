import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus, AlertCircle, History } from 'lucide-react';

export default function WhatChangedWidget({ data }) {
  if (!data) return null;

  const {
    volume_yesterday,
    volume_previous_day,
    volume_delta_pct,
    critical_delta,
    top_app_name,
    top_app_delta_pct,
    breach_delta_pct,
    active_patterns,
    insights
  } = data;

  const renderTrendBadge = (val, suffix = '%') => {
    if (val > 0) {
      return (
        <span className="inline-flex items-center text-rose-600 font-semibold text-xs">
          <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
          +{val}{suffix}
        </span>
      );
    } else if (val < 0) {
      return (
        <span className="inline-flex items-center text-emerald-600 font-semibold text-xs">
          <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
          {val}{suffix}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center text-slate-500 font-semibold text-xs">
        <Minus className="w-3.5 h-3.5 mr-0.5" />
        0{suffix}
      </span>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <History className="w-4 h-4 text-slate-500" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            What Changed Since Yesterday?
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Ref: {data.reference_date} vs Prior Day
        </span>
      </div>

      {/* Delta KPI Chips */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        <div className="bg-slate-50 border border-slate-200/80 rounded p-2.5">
          <div className="text-[11px] text-slate-500 font-medium">Volume Shift</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-base font-bold text-slate-900">{volume_yesterday}</span>
            {renderTrendBadge(volume_delta_pct)}
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200/80 rounded p-2.5">
          <div className="text-[11px] text-slate-500 font-medium">Critical (P1) Shift</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-base font-bold text-slate-900">{data.critical_yesterday}</span>
            <span className={`text-xs font-semibold ${critical_delta > 0 ? 'text-rose-600' : 'text-slate-600'}`}>
              {critical_delta >= 0 ? `+${critical_delta}` : critical_delta} net
            </span>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200/80 rounded p-2.5">
          <div className="text-[11px] text-slate-500 font-medium truncate" title={top_app_name}>
            {top_app_name}
          </div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-base font-bold text-slate-900">{data.top_app_count}</span>
            {renderTrendBadge(top_app_delta_pct)}
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200/80 rounded p-2.5">
          <div className="text-[11px] text-slate-500 font-medium">SLA Breaches</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-base font-bold text-slate-900">{data.breach_yesterday}</span>
            {renderTrendBadge(breach_delta_pct)}
          </div>
        </div>
      </div>

      {/* Bulleted Insights */}
      <div className="space-y-1.5 border-t border-slate-100 pt-3">
        {insights.map((ins, idx) => (
          <div key={idx} className="flex items-start space-x-2 text-xs text-slate-700">
            <span className="text-blue-500 font-bold leading-none mt-0.5">•</span>
            <span>{ins}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
