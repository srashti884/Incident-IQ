import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const api = {
  // System Status & Health
  getSystemStatus: () => client.get('/analytics/system-status').then(r => r.data),
  getHealth: () => client.get('/health').then(r => r.data),

  // Analytics & Dashboard
  getDashboard: () => client.get('/analytics/dashboard').then(r => r.data),
  getWhatChanged: () => client.get('/analytics/what-changed').then(r => r.data),
  getImpactMatrix: (limit = 150) => client.get('/analytics/impact-matrix', { params: { limit } }).then(r => r.data),

  // Natural Language & Voice
  executeNLQuery: (query) => client.post('/nlp/query', { query }).then(r => r.data),
  getSuggestedExamples: () => client.get('/nlp/examples').then(r => r.data),
  transcribeAudio: (formData) => client.post('/nlp/voice/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(r => r.data),

  // Incident Explorer
  getIncidents: (params) => client.get('/incidents', { params }).then(r => r.data),
  getIncidentFilters: () => client.get('/incidents/filters').then(r => r.data),
  getIncidentStory: (id) => client.get(`/incidents/${id}/story`).then(r => r.data),

  // Patterns
  getPatterns: () => client.get('/patterns').then(r => r.data),
  getPatternIncidents: (id) => client.get(`/patterns/${id}/incidents`).then(r => r.data),

  // Reporting Downloads (blobs)
  downloadQueryPdf: async (queryResult) => {
    const response = await client.post('/reports/query-pdf', queryResult, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `IncidentIQ_Query_Result_${new Date().toISOString().slice(0, 10)}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  downloadGeneralPdf: async (scope = {}) => {
    const response = await client.post('/reports/general-pdf', scope, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `IncidentIQ_Executive_Report_${new Date().toISOString().slice(0, 10)}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  downloadExcel: async (app = null) => {
    const params = app ? { app } : {};
    const response = await client.get('/reports/excel', { params, responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `IncidentIQ_Export_${new Date().toISOString().slice(0, 10)}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  downloadCsv: async (records = null, application = null) => {
    const response = await client.post('/reports/csv', { records, application }, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `IncidentIQ_Export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  // MCP Tools
  getMcpTools: () => client.get('/mcp/tools').then(r => r.data),
  invokeMcpTool: (tool, args = {}) => client.post('/mcp/invoke', { tool, arguments: args }).then(r => r.data),
};
