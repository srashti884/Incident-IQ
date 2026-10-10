import React, { useState, useEffect } from 'react';
import { Database, CheckCircle, Server, Terminal, Shield, FileCode, Play } from 'lucide-react';
import { api } from '../services/api';

export default function SystemWarehousePage({ warehouseStats }) {
  const [mcpTools, setMcpTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState('');
  const [toolArgs, setToolArgs] = useState('{}');
  const [mcpResult, setMcpResult] = useState(null);
  const [mcpExecuting, setMcpExecuting] = useState(false);

  useEffect(() => {
    api.getMcpTools().then(res => {
      setMcpTools(res.tools || []);
      if (res.tools && res.tools.length > 0) {
        setSelectedTool(res.tools[0].name);
      }
    }).catch(() => {});
  }, []);

  const handleExecuteMcp = async () => {
    if (!selectedTool) return;
    setMcpExecuting(true);
    setMcpResult(null);
    try {
      let parsedArgs = {};
      try {
        parsedArgs = JSON.parse(toolArgs);
      } catch (err) {
        alert('Invalid JSON in tool arguments: ' + err.message);
        setMcpExecuting(false);
        return;
      }
      const res = await api.invokeMcpTool(selectedTool, parsedArgs);
      setMcpResult(res);
    } catch (err) {
      setMcpResult({ error: err.message });
    } finally {
      setMcpExecuting(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-2">
            <Database className="w-4 h-4 text-blue-600" />
            <span>Local Warehouse Architecture & MCP Layer</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            SQLite Lakehouse infrastructure, WAL-mode indexing, and decoupled local Model Context Protocol tools.
          </p>
        </div>
        <div className="text-right text-xs font-mono text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200 font-semibold">
          100% AIR-GAPPED &bull; LOCAL ONLY
        </div>
      </div>

      {/* Warehouse Status Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Warehouse File Size
          </span>
          <div className="text-xl font-bold text-slate-900 font-mono">
            {warehouseStats?.file_size_kb || 0} <span className="text-xs text-slate-500">KB</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Single Portable SQLite File</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Total Incident Records
          </span>
          <div className="text-xl font-bold text-slate-900 font-mono">
            {warehouseStats?.total_incidents?.toLocaleString() || 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">B-Tree Indexed Schema</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Cataloged Applications
          </span>
          <div className="text-xl font-bold text-slate-900 font-mono">
            {warehouseStats?.total_applications || 0} Systems
          </div>
          <div className="text-[10px] text-slate-400 mt-1">19 Subservice Components</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Recurring Pattern Profiles
          </span>
          <div className="text-xl font-bold text-slate-900 font-mono">
            {warehouseStats?.total_patterns || 0} Fingerprints
          </div>
          <div className="text-[10px] text-slate-400 mt-1">TF-IDF Vectorized Clusters</div>
        </div>

      </div>

      {/* Local MCP Tool Runner */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-1.5">
              <Terminal className="w-4 h-4 text-blue-600" />
              <span>Local Model Context Protocol (MCP) Tool Test Bench</span>
            </h3>
            <div className="text-[11px] text-slate-400 mt-0.5">
              Execute standardized local analytical tools without external MCP servers or cloud intermediaries.
            </div>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {mcpTools.length} Local Tools Registered
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Tool Selector & Arguments Input */}
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Select Local MCP Tool:</label>
              <select
                value={selectedTool}
                onChange={(e) => setSelectedTool(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-300 rounded text-xs font-mono text-slate-800 focus:bg-white"
              >
                {mcpTools.map(t => (
                  <option key={t.name} value={t.name}>{t.name}()</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Tool Arguments (JSON):</label>
              <textarea
                rows="4"
                value={toolArgs}
                onChange={(e) => setToolArgs(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 text-emerald-400 font-mono text-xs rounded border border-slate-800 focus:outline-hidden"
                placeholder='{"limit": 5}'
              />
            </div>

            <button
              onClick={handleExecuteMcp}
              disabled={mcpExecuting || !selectedTool}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded transition shadow-xs cursor-pointer flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{mcpExecuting ? 'Executing Tool...' : 'Invoke Local MCP Tool'}</span>
            </button>
          </div>

          {/* Execution Result Output */}
          <div className="bg-slate-950 border border-slate-800 rounded p-3 flex flex-col h-64 overflow-hidden">
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-widest pb-1 border-b border-slate-800 mb-2">
              Tool Output Stream (JSON-RPC)
            </div>
            <pre className="flex-1 font-mono text-[11px] text-slate-300 overflow-y-auto leading-relaxed">
              {mcpResult ? JSON.stringify(mcpResult, null, 2) : '// Click "Invoke Local MCP Tool" to inspect response...'}
            </pre>
          </div>

        </div>

      </div>

      {/* Semantic Layer Architecture Description */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center space-x-1.5">
          <FileCode className="w-4 h-4 text-slate-600" />
          <span>Semantic Data Layer Architecture</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          IncidentIQ bridges natural language queries with the SQLite Lakehouse through three declarative metadata files:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="bg-slate-50 border border-slate-200 rounded p-3">
            <span className="font-bold text-slate-900 font-mono block mb-1">semantic/glossary.json</span>
            <span className="text-slate-500">Defines domain vocabulary (MTTR, SLA breach, recurring incident, root cause) and synonyms.</span>
          </div>
          <div className="bg-slate-50 border border-slate-200 rounded p-3">
            <span className="font-bold text-slate-900 font-mono block mb-1">semantic/mappings.json</span>
            <span className="text-slate-500">Maps free-text aliases ('aws' &rarr; 'AWS Cloud Infrastructure', 'p1' &rarr; 'Critical', 'open' &rarr; status).</span>
          </div>
          <div className="bg-slate-50 border border-slate-200 rounded p-3">
            <span className="font-bold text-slate-900 font-mono block mb-1">semantic/metrics.json</span>
            <span className="text-slate-500">Houses formal calculation formulas (MTTR, SLA Breach Rate %, Total Volume, Impact Score).</span>
          </div>
        </div>
      </div>

    </div>
  );
}
