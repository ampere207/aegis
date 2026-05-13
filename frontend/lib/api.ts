// API client abstraction for frontend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async get(endpoint: string) {
    const res = await fetch(`${API_BASE}${endpoint}`, { credentials: 'include' });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },

  async post(endpoint: string, data: any) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return res.json();
  },
};
