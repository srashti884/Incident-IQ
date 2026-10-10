import React, { useState, useEffect } from 'react';
import { FileText, Download, FileSpreadsheet, CheckCircle2, ShieldCheck, Database, Calendar } from 'lucide-react';
import { api } from '../services/api';

export default function ReportsPage() {
  const [apps, setApps] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [timeHorizon, setTimeHorizon] = useState('all');
  const [isPdfLoading, setIsPdfLoading] = useState(false);
  const [isExcelLoading, setIsExcelLoading] = useState(false);
  const [isCsvLoading, setIsCsvLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  useEffect(() => {
    api.getIncidentFilters().then(data => setApps(data.applications || [])).catch(() => {});
  }, []);

  const handleGeneratePdf = async () => {
    setIsPdfLoading(true);
    setStatusMsg(null);
    try {
      await api.downloadGeneralPdf({ application: selectedApp || null, horizon: timeHorizon });
      setStatusMsg({ type: 'success', text: 'Executive Audit PDF compiled and downloaded successfully via ReportLab.' });
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'PDF compilation failed: ' + err.message });
    } finally {
      setIsPdfLoading(false);
    }
  };

  const handleExportExcel = async () => {
    setIsExcelLoading(true);
    setStatusMsg(null);
    try {
      await api.downloadExcel(selectedApp || null);
      setStatusMsg({ type: 'success', text: 'Multi-sheet workbook compiled and downloaded successfully via OpenPyXL.' });
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Excel compilation failed: ' + err.message });
    } finally {
      setIsExcelLoading(false);
    }
  };

  const handleExportCsv = async () => {
    setIsCsvLoading(true);
    setStatusMsg(null);
    try {
      await api.downloadCsv(null, selectedApp || null);
      setStatusMsg({ type: 'success', text: 'Raw incident CSV exported successfully.' });
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'CSV export failed: ' + err.message });
    } finally {
      setIsCsvLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-2">
            <FileText className="w-4 h-4 text-blue-600" />
            <span>Executive Reporting & Regulatory Audit Hub</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Produce verified, paginated ReportLab executive reports and OpenPyXL workbooks completely offline.
          </p>
        </div>
        <div className="text-right text-xs font-mono text-emerald-600 font-semibold bg-emerald-50 px-2 py-1 rounded border border-emerald-200">
          ReportLab 5.0 Local Engine Active
        </div>
      </div>

      {statusMsg && (
        <div className={`p-4 rounded text-xs border ${
          statusMsg.type === 'success' 
            ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
            : 'bg-rose-50 text-rose-800 border-rose-200'
        }`}>
          {statusMsg.text}
        </div>
      )}

      {/* Scope Configuration */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
          Report Parameter Configuration
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-600 font-medium mb-1">Target Application Portfolio:</label>
            <select
              value={selectedApp}
              onChange={(e) => setSelectedApp(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded text-slate-800 focus:bg-white"
            >
              <option value="">All Applications (Enterprise Scope)</option>
              {apps.map(a => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-600 font-medium mb-1">Audit Horizon Period:</label>
            <select
              value={timeHorizon}
              onChange={(e) => setTimeHorizon(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded text-slate-800 focus:bg-white"
            >
              <option value="all">Full Warehouse History (Trailing 180 Days)</option>
              <option value="q3">Current Quarter (Q3 2026)</option>
              <option value="last30">Last 30 Days</option>
              <option value="last7">Last 7 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Export Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* PDF Executive Report */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 bg-slate-900 text-white rounded flex items-center justify-center mb-3">
              <FileText className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900">Executive Audit PDF</h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Complete paginated PDF report featuring executive KPI summaries, What Changed highlights, application health rankings, and recurring patterns.
            </p>
          </div>
          <button
            onClick={handleGeneratePdf}
            disabled={isPdfLoading}
            className="mt-5 w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded transition shadow-xs cursor-pointer flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isPdfLoading ? 'Generating PDF...' : 'Download Executive PDF'}</span>
          </button>
        </div>

        {/* Excel Analytical Workbook */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 bg-emerald-700 text-white rounded flex items-center justify-center mb-3">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900">Full Excel Workbook</h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Styled multi-sheet OpenPyXL workbook containing raw incident log, application summary metrics, and recurring pattern catalogs with auto-fit columns.
            </p>
          </div>
          <button
            onClick={handleExportExcel}
            disabled={isExcelLoading}
            className="mt-5 w-full py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold rounded transition shadow-xs cursor-pointer flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isExcelLoading ? 'Generating XLSX...' : 'Download Excel (.xlsx)'}</span>
          </button>
        </div>

        {/* CSV Data Dump */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 bg-blue-600 text-white rounded flex items-center justify-center mb-3">
              <Database className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900">Raw Incident CSV</h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Standard RFC-4180 flat CSV export containing all filtered operational ticket fields for external tool interoperability or custom pipeline ingestion.
            </p>
          </div>
          <button
            onClick={handleExportCsv}
            disabled={isCsvLoading}
            className="mt-5 w-full py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded transition shadow-xs cursor-pointer flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isCsvLoading ? 'Exporting...' : 'Export Flat CSV'}</span>
          </button>
        </div>

      </div>

    </div>
  );
}
