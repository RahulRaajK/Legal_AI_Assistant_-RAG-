/**
 * API client for Legal AI Assistant backend.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
    constructor() { }

    setToken(token: string) {
        if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', token);
        }
    }

    clearToken() {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
        }
    }

    private async request(path: string, options: RequestInit = {}) {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string> || {}),
        };

        let currentToken = null;
        if (typeof window !== 'undefined') {
            currentToken = localStorage.getItem('auth_token');
        }

        if (currentToken) {
            headers['Authorization'] = `Bearer ${currentToken}`;
        }

        const response = await fetch(`${API_BASE}${path}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Auth
    async register(data: { email: string; username: string; full_name: string; password: string; role: string }) {
        const result = await this.request('/api/auth/register', { method: 'POST', body: JSON.stringify(data) });
        this.setToken(result.access_token);
        return result;
    }

    async login(username: string, password: string) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });

        if (!response.ok) throw new Error('Login failed');
        const result = await response.json();
        this.setToken(result.access_token);
        return result;
    }

    async getMe() {
        return this.request('/api/auth/me');
    }

    async getLawyers() {
        return this.request('/api/auth/lawyers');
    }

    async updateProfile(data: any) {
        return this.request('/api/auth/profile', { method: 'PUT', body: JSON.stringify(data) });
    }

    // Calendar
    async getHolidays() {
        return this.request('/api/calendar/holidays');
    }

    // Chat
    async sendMessage(message: string, sessionId?: string, userRole?: string) {
        return this.request('/api/chat/send', {
            method: 'POST',
            body: JSON.stringify({ message, session_id: sessionId, user_role: userRole }),
        });
    }

    async getChatSessions() {
        return this.request('/api/chat/sessions');
    }

    async getSessionMessages(sessionId: string) {
        return this.request(`/api/chat/sessions/${sessionId}/messages`);
    }

    // Cases
    async createCase(data: any) {
        return this.request('/api/cases/', { method: 'POST', body: JSON.stringify(data) });
    }

    async getCases(status?: string) {
        const params = status ? `?status=${status}` : '';
        return this.request(`/api/cases/${params}`);
    }

    async getCase(caseId: string) {
        return this.request(`/api/cases/${caseId}`);
    }

    async updateCase(id: string, data: any) {
        return this.request(`/api/cases/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async analyzeCase(caseId: string) {
        return this.request(`/api/cases/${caseId}/analyze`, { method: 'POST' });
    }

    // Documents
    async uploadDocument(file: File, caseId?: string, documentType?: string) {
        const formData = new FormData();
        formData.append('file', file);
        if (caseId) formData.append('case_id', caseId);
        if (documentType) formData.append('document_type', documentType);

        let currentToken = null;
        if (typeof window !== 'undefined') {
            currentToken = localStorage.getItem('auth_token');
        }

        const headers: Record<string, string> = {};
        if (currentToken) headers['Authorization'] = `Bearer ${currentToken}`;

        const response = await fetch(`${API_BASE}/api/documents/upload`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) throw new Error('Upload failed');
        return response.json();
    }

    async analyzeDocument(documentId: string, question?: string) {
        return this.request(`/api/documents/${documentId}/analyze`, {
            method: 'POST',
            body: JSON.stringify({ question }),
        });
    }

    async updateAdmissibility(documentId: string, status: string) {
        return this.request(`/api/documents/${documentId}/admissibility`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
    }

    async getDocuments(caseId?: string) {
        const params = caseId ? `?case_id=${caseId}` : '';
        return this.request(`/api/documents/${params}`);
    }

    async buildArguments(documentId: string, side: string, context?: string) {
        const formData = new URLSearchParams();
        formData.append("side", side);
        if (context) formData.append("context", context);

        let currentToken = null;
        if (typeof window !== 'undefined') {
            currentToken = localStorage.getItem('auth_token');
        }

        const response = await fetch(`${API_BASE}/api/documents/${documentId}/build-arguments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                ...(currentToken ? { 'Authorization': `Bearer ${currentToken}` } : {})
            },
            body: formData,
        });

        if (!response.ok) throw new Error('Argument generation failed');
        return response.json();
    }

    // Search
    async semanticSearch(query: string, n: number = 10, contentType?: string) {
        const params = new URLSearchParams({ q: query, n: n.toString() });
        if (contentType) params.append('content_type', contentType);
        return this.request(`/api/search/semantic?${params}`);
    }

    async searchStatutes(query: string) {
        return this.request(`/api/search/statutes?q=${encodeURIComponent(query)}`);
    }

    async searchCases(query: string) {
        return this.request(`/api/search/cases?q=${encodeURIComponent(query)}`);
    }

    async searchGraph(query: string, nodeType?: string) {
        const params = new URLSearchParams({ q: query });
        if (nodeType) params.append('node_type', nodeType);
        return this.request(`/api/search/graph?${params}`);
    }

    async getSearchStats() {
        return this.request('/api/search/stats');
    }

    // Health
    async healthCheck() {
        return this.request('/api/health');
    }

    async getModels() {
        return this.request('/api/models');
    }

    // Crawler
    async crawlSearch(source: string, query: string) {
        return this.request('/api/crawler/search', {
            method: 'POST',
            body: JSON.stringify({ source, query }),
        });
    }

    async fetchAndIngest(url: string, source: string) {
        return this.request('/api/crawler/fetch-and-ingest', {
            method: 'POST',
            body: JSON.stringify({ url, source }),
        });
    }

    async checkAmendments() {
        return this.request('/api/crawler/check-amendments', { method: 'POST' });
    }
}

export const api = new ApiClient();
export default api;
