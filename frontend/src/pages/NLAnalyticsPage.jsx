import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Mic, 
  MicOff, 
  Download, 
  FileSpreadsheet, 
  Clock, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  ChevronRight,
  Filter,
  BarChart2
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
  Legend 
} from 'recharts';
import { api } from '../services/api';

const SUGGESTED_QUERIES = [
  "What incidents were reported yesterday?",
  "Show all critical incidents from last week.",
  "Which applications generated the most incidents this quarter?",
  "Show AWS incidents from last month.",
  "Which applications have the highest SLA breaches?",
  "Identify recurring incidents.",
  "What are the most common root causes?",
  "Which services have the longest resolution time?",
  "Show me unresolved critical incidents."
];

export default function NLAnalyticsPage({ onSelectIncident }) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isPdfGenerating, setIsPdfGenerating] = useState(false);
  const [isCsvGenerating, setIsCsvGenerating] = useState(false);

  // Voice recording state
  const [isListening, setIsListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState(''); // 'Listening...', 'Processing...', 'Transcription complete.'
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check if Web Speech API is supported in local browser
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setVoiceStatus('Listening...');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setQuery(transcript);
        setVoiceStatus('Transcription complete.');
        setIsListening(false);
        // Automatically run pipeline
        handleAnalyze(transcript);
      };

      recognition.onerror = (event) => {
        setIsListening(false);
        if (event.error === 'not-allowed') {
          setVoiceStatus('Microphone permission denied. Typed query remains operational.');
        } else {
          setVoiceStatus(`Microphone unavailable (${event.error}). Use typed input.`);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceRecording = () => {
    if (!recognitionRef.current) {
      setVoiceStatus('Speech recognition not supported in this browser. Please type your query.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      setVoiceStatus('Processing...');
    } else {
      setVoiceStatus('Listening...');
      setError(null);
      try {
        recognitionRef.current.start();
      } catch (err) {
        setIsListening(false);
        setVoiceStatus('Could not access microphone. Typed query is active.');
      }
    }
  };

  const handleAnalyze = async (queryToRun = query) => {
    const q = queryToRun.trim();
    if (!q) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await api.executeNLQuery(q);
      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || "I couldn't confidently interpret this query.");
        setResult(null);
      }
    } catch (err) {
      setError('Query execution failed: ' + err.message);
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  const handleDownloadPdf = async () => {
    if (!result) return;
    setIsPdfGenerating(true);
    try {
      await api.downloadQueryPdf(result);
    } catch (err) {
      alert('Local PDF generation failed: ' + err.message);
    } finally {
      setIsPdfGenerating(false);
    }
  };

  const handleExportCsv = async () => {
    if (!result || !result.table_data) return;
    setIsCsvGenerating(true);
    try {
      await api.downloadCsv(result.table_data);
    } catch (err) {
      alert('CSV export failed: ' + err.message);
    } finally {
      setIsCsvGenerating(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Query Input Section */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
          Natural Language Incident Analytics Query
        </label>
        
        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your incidents in natural language..."
              className="w-full pl-4 pr-11 py-2.5 bg-slate-50 border border-slate-300 rounded text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-600 focus:bg-white transition"
            />
            {/* Microphone Button */}
            <button
              type="button"
              onClick={toggleVoiceRecording}
              className={`absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 rounded transition cursor-pointer ${
                isListening 
                  ? 'bg-rose-600 text-white animate-pulse' 
                  : 'text-slate-400 hover:text-slate-700 hover:bg-slate-200'
              }`}
              title={isListening ? 'Stop voice recording' : 'Speak your query via microphone'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          </div>

          <button
            onClick={() => handleAnalyze()}
            disabled={isLoading || !query.trim()}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded disabled:opacity-50 transition shadow-xs cursor-pointer flex items-center space-x-1.5 shrink-0"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>

        {/* Voice Feedback Message */}
        {voiceStatus && (
          <div className="mt-2 text-xs font-mono text-blue-600 flex items-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
            <span>{voiceStatus}</span>
          </div>
        )}

        {/* Suggested Queries */}
        <div className="mt-4 pt-3 border-t border-slate-100">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Suggested Operational Inquiries
          </div>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_QUERIES.map((sq, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(sq);
                  handleAnalyze(sq);
                }}
                className="px-2.5 py-1 text-xs text-slate-600 bg-slate-100 hover:bg-slate-200 hover:text-slate-900 border border-slate-200 rounded transition cursor-pointer"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-amber-50 border border-amber-200 text-amber-900 p-4 rounded text-sm">
          <div className="font-semibold flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>Query Resolution Notice</span>
          </div>
          <div className="mt-1 text-amber-800">{error}</div>
        </div>
      )}

      {/* Query Understanding Panel */}
      {result && (
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-5">
          
          {/* Explainability Bar */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Query Understanding & Execution Plan
              </span>
              <h2 className="text-sm font-semibold text-slate-800 mt-0.5">
                {result.summary}
              </h2>
            </div>
            
            {/* Direct Export Action Bar */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownloadPdf}
                disabled={isPdfGenerating}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded transition cursor-pointer shadow-xs disabled:opacity-50"
                title="Download verified ReportLab PDF for this exact query result"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{isPdfGenerating ? 'Compiling PDF...' : 'Download Result as PDF'}</span>
              </button>

              <button
                onClick={handleExportCsv}
                disabled={isCsvGenerating}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded transition cursor-pointer disabled:opacity-50"
                title="Export active records to CSV"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-slate-500" />
                <span>{isCsvGenerating ? 'Exporting...' : 'Export CSV'}</span>
              </button>
            </div>
          </div>

          {/* Explainability Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 bg-slate-50 border border-slate-200 rounded p-3 text-xs">
            <div>
              <span className="text-slate-400 font-medium">Classified Intent:</span>
              <div className="font-semibold text-slate-800 font-mono mt-0.5">
                {result.query_understanding.intent}
              </div>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Application Scope:</span>
              <div className="font-semibold text-slate-800 truncate mt-0.5">
                {result.query_understanding.entities.application || 'All Applications'}
              </div>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Severity Constraint:</span>
              <div className="font-semibold text-slate-800 mt-0.5">
                {result.query_understanding.entities.severity || 'Unconstrained'}
              </div>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Temporal Range:</span>
              <div className="font-semibold text-slate-800 mt-0.5">
                {result.query_understanding.entities.time_range || 'All History'}
              </div>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Warehouse Engine:</span>
              <div className="font-semibold text-slate-800 mt-0.5">
                SQLite B-Tree Index
              </div>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Latency:</span>
              <div className="font-mono font-bold text-emerald-600 mt-0.5">
                {result.query_understanding.execution_time_ms} ms
              </div>
            </div>
          </div>

          {/* Applied Filters Tags */}
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-medium">Applied Filters:</span>
            <div className="flex flex-wrap gap-1">
              {result.applied_filters.map((f, idx) => (
                <span key={idx} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px] font-medium border border-slate-200">
                  {f}
                </span>
              ))}
            </div>
          </div>

          {/* Visual Chart If Applicable */}
          {result.chart_data && result.chart_data.length > 0 && (
            <div className="border border-slate-200 rounded p-4">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center space-x-1.5">
                <BarChart2 className="w-4 h-4 text-blue-600" />
                <span>{result.chart_config.title || 'Analytical Visualization'}</span>
              </div>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  {result.chart_config.type === 'line' ? (
                    <LineChart data={result.chart_data} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey={result.chart_config.x_key} tick={{ fontSize: 10, fill: '#64748b' }} />
                      <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }} />
                      <Line type="monotone" dataKey={result.chart_config.y_key} stroke="#2563EB" strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                  ) : (
                    <BarChart data={result.chart_data.slice(0, 10)} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey={result.chart_config.x_key} tick={{ fontSize: 10, fill: '#64748b' }} />
                      <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontSize: '11px', borderRadius: '4px' }} />
                      <Bar dataKey={result.chart_config.y_key} fill="#2563EB" radius={[2, 2, 0, 0]} />
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Results Table */}
          {result.table_data && result.table_data.length > 0 && (
            <div className="border border-slate-200 rounded overflow-hidden">
              <div className="bg-slate-50 px-4 py-2.5 border-b border-slate-200 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Result Records ({result.table_data.length.toLocaleString()})
                </span>
                <span className="text-[11px] text-slate-400">Click row for full story & timeline</span>
              </div>
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left border-collapse text-xs">
                  <thead className="bg-slate-900 text-white sticky top-0 z-10">
                    <tr>
                      {result.view_type === 'grouped_analytics' ? (
                        <>
                          <th className="px-4 py-2 font-semibold">Dimension</th>
                          <th className="px-4 py-2 font-semibold">Metric Value</th>
                          <th className="px-4 py-2 font-semibold">Total Volume</th>
                        </>
                      ) : result.view_type === 'patterns' ? (
                        <>
                          <th className="px-4 py-2 font-semibold">Pattern ID</th>
                          <th className="px-4 py-2 font-semibold">Fingerprint</th>
                          <th className="px-4 py-2 font-semibold">Occurrences</th>
                          <th className="px-4 py-2 font-semibold">Trend</th>
                          <th className="px-4 py-2 font-semibold">Avg Resolution</th>
                        </>
                      ) : (
                        <>
                          <th className="px-3 py-2 font-semibold">ID</th>
                          <th className="px-3 py-2 font-semibold">Title</th>
                          <th className="px-3 py-2 font-semibold">Application</th>
                          <th className="px-3 py-2 font-semibold">Severity</th>
                          <th className="px-3 py-2 font-semibold">Status</th>
                          <th className="px-3 py-2 font-semibold">Created At</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {result.table_data.map((row, idx) => (
                      <tr 
                        key={idx} 
                        onClick={() => row.incident_id && onSelectIncident && onSelectIncident(row.incident_id)}
                        className={`hover:bg-blue-50/60 transition ${row.incident_id ? 'cursor-pointer' : ''}`}
                      >
                        {result.view_type === 'grouped_analytics' ? (
                          <>
                            <td className="px-4 py-2 font-semibold text-slate-900">{row.dimension}</td>
                            <td className="px-4 py-2 font-mono text-blue-600 font-bold">{row.metric_value}</td>
                            <td className="px-4 py-2 text-slate-600">{row.incident_count}</td>
                          </>
                        ) : result.view_type === 'patterns' ? (
                          <>
                            <td className="px-4 py-2 font-mono font-bold text-slate-900">{row.pattern_id}</td>
                            <td className="px-4 py-2 font-medium text-slate-800">{row.fingerprint}</td>
                            <td className="px-4 py-2 font-bold text-slate-900">{row.occurrences}</td>
                            <td className="px-4 py-2">
                              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                                {row.trend}
                              </span>
                            </td>
                            <td className="px-4 py-2 font-mono text-slate-600">{row.avg_resolution_minutes}m</td>
                          </>
                        ) : (
                          <>
                            <td className="px-3 py-2 font-mono font-bold text-blue-600">{row.incident_id}</td>
                            <td className="px-3 py-2 font-medium text-slate-900 max-w-xs truncate" title={row.title}>{row.title}</td>
                            <td className="px-3 py-2 text-slate-600">{row.application}</td>
                            <td className="px-3 py-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                row.severity === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                                row.severity === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                                'bg-slate-100 text-slate-700'
                              }`}>
                                {row.severity}
                              </span>
                            </td>
                            <td className="px-3 py-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                                row.status === 'Open' ? 'bg-rose-100 text-rose-800' :
                                row.status === 'In Progress' ? 'bg-amber-100 text-amber-800' :
                                'bg-emerald-100 text-emerald-800'
                              }`}>
                                {row.status}
                              </span>
                            </td>
                            <td className="px-3 py-2 font-mono text-slate-500">{row.created_at?.slice(0, 16)}</td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
