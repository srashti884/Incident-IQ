import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Filter, Download, ChevronLeft, ChevronRight, RefreshCw, Layers } from 'lucide-react';
import { api } from '../services/api';

export default function IncidentExplorerPage({ onSelectIncident }) {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [incidents, setIncidents] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterOptions, setFilterOptions] = useState({ applications: [], severities: [], statuses: [] });

  // Filters state initialized from searchParams if present
  const [searchTerm, setSearchTerm] = useState(searchParams.get('q') || '');
  const [appFilter, setAppFilter] = useState(searchParams.get('application') || '');
  const [sevFilter, setSevFilter] = useState(searchParams.get('severity') || '');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');
  const [slaFilter, setSlaFilter] = useState(searchParams.get('sla_breached') || '');

  // Pagination
  const [limit, setLimit] = useState(25);
  const [offset, setOffset] = useState(0);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    api.getIncidentFilters().then(data => setFilterOptions(data)).catch(() => {});
  }, []);

  useEffect(() => {
    fetchIncidents();
  }, [appFilter, sevFilter, statusFilter, slaFilter, limit, offset]);

  // Debounced text search
  useEffect(() => {
    const handler = setTimeout(() => {
      fetchIncidents();
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params = {
        limit,
        offset,
        q: searchTerm || undefined,
        application: appFilter || undefined,
        severity: sevFilter || undefined,
        status: statusFilter || undefined,
        sla_breached: slaFilter !== '' ? parseInt(slaFilter, 10) : undefined
      };
      const data = await api.getIncidents(params);
      setIncidents(data.results || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error('Error fetching incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = async () => {
    setIsExporting(true);
    try {
      await api.downloadCsv(incidents, appFilter || null);
    } catch (err) {
      alert('CSV export failed: ' + err.message);
    } finally {
      setIsExporting(false);
    }
  };

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(totalCount / limit) || 1;

  return (
    <div className="p-6 space-y-5 max-w-7xl mx-auto">
      
      {/* Filters Toolbar */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
          
          {/* Search Input */}
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setOffset(0); }}
              placeholder="Search by incident ID, summary, keywords..."
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded focus:bg-white focus:outline-hidden focus:ring-1 focus:ring-blue-600 transition"
            />
          </div>

          {/* Export & Stats */}
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={handleExportCsv}
              disabled={isExporting || incidents.length === 0}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded hover:bg-slate-50 transition cursor-pointer disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              <span>{isExporting ? 'Exporting...' : 'Export Filtered CSV'}</span>
            </button>
          </div>

        </div>

        {/* Dropdown Filters Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100 text-xs">
          
          {/* Application */}
          <select
            value={appFilter}
            onChange={(e) => { setAppFilter(e.target.value); setOffset(0); }}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded text-slate-800"
          >
            <option value="">All Applications</option>
            {filterOptions.applications.map(a => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>

          {/* Severity */}
          <select
            value={sevFilter}
            onChange={(e) => { setSevFilter(e.target.value); setOffset(0); }}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded text-slate-800"
          >
            <option value="">All Severities</option>
            {filterOptions.severities.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          {/* Status */}
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setOffset(0); }}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded text-slate-800"
          >
            <option value="">All Statuses</option>
            {filterOptions.statuses.map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>

          {/* SLA Breached */}
          <select
            value={slaFilter}
            onChange={(e) => { setSlaFilter(e.target.value); setOffset(0); }}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-300 rounded text-slate-800"
          >
            <option value="">All SLA Records</option>
            <option value="1">SLA Breached Only</option>
            <option value="0">Within SLA Only</option>
          </select>

        </div>
      </div>

      {/* Incident Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
        <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>
            Showing <strong className="text-slate-800 font-semibold">{incidents.length}</strong> of <strong className="text-slate-800 font-semibold">{totalCount.toLocaleString()}</strong> incidents
          </span>
          <span className="text-[11px] text-slate-400">Click any row to open incident story drill-down</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="bg-slate-900 text-white select-none">
              <tr>
                <th className="px-3 py-2.5 font-semibold">Incident ID</th>
                <th className="px-3 py-2.5 font-semibold">Title</th>
                <th className="px-3 py-2.5 font-semibold">Application</th>
                <th className="px-3 py-2.5 font-semibold">Service</th>
                <th className="px-3 py-2.5 font-semibold">Severity</th>
                <th className="px-3 py-2.5 font-semibold">Status</th>
                <th className="px-3 py-2.5 font-semibold">Created At</th>
                <th className="px-3 py-2.5 font-semibold">MTTR</th>
                <th className="px-3 py-2.5 font-semibold">SLA</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="9" className="px-4 py-8 text-center text-slate-400">
                    <div className="flex items-center justify-center space-x-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                      <span>Loading records from local warehouse...</span>
                    </div>
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-4 py-8 text-center text-slate-400">
                    No incidents found matching active filters.
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr
                    key={inc.incident_id}
                    onClick={() => onSelectIncident(inc.incident_id)}
                    className="hover:bg-blue-50/60 transition cursor-pointer"
                  >
                    <td className="px-3 py-2.5 font-mono font-bold text-blue-600">{inc.incident_id}</td>
                    <td className="px-3 py-2.5 font-medium text-slate-900 max-w-xs truncate" title={inc.title}>
                      {inc.title}
                    </td>
                    <td className="px-3 py-2.5 text-slate-700">{inc.application}</td>
                    <td className="px-3 py-2.5 text-slate-500">{inc.service}</td>
                    <td className="px-3 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inc.severity === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        inc.severity === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="px-3 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                        inc.status === 'Open' ? 'bg-rose-100 text-rose-800' :
                        inc.status === 'In Progress' ? 'bg-amber-100 text-amber-800' :
                        'bg-emerald-100 text-emerald-800'
                      }`}>
                        {inc.status}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 font-mono text-slate-500">{inc.created_at?.slice(0, 16)}</td>
                    <td className="px-3 py-2.5 font-mono text-slate-700">
                      {inc.resolution_time_minutes ? `${inc.resolution_time_minutes}m` : '—'}
                    </td>
                    <td className="px-3 py-2.5">
                      {inc.sla_breached === 1 ? (
                        <span className="text-[10px] font-bold text-rose-600 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded">
                          BREACH
                        </span>
                      ) : (
                        <span className="text-[10px] font-medium text-emerald-600">
                          OK
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <span className="text-slate-500">Rows per page:</span>
            <select
              value={limit}
              onChange={(e) => { setLimit(Number(e.target.value)); setOffset(0); }}
              className="px-2 py-1 bg-white border border-slate-300 rounded text-slate-700"
            >
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-slate-500">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0 || loading}
                className="p-1 rounded border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 transition cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4 text-slate-600" />
              </button>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= totalCount || loading}
                className="p-1 rounded border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 transition cursor-pointer"
              >
                <ChevronRight className="w-4 h-4 text-slate-600" />
              </button>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
