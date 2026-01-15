import type { GlobalConfig, SiteConfig, FetchSummaryResponse } from '../types';

const API_BASE = '/api';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

export const api = {
  getSchema: async (): Promise<Record<string, unknown>> => {
    const response = await fetch(`${API_BASE}/config/schema`);
    return handleResponse(response);
  },

  getGlobalConfig: async (): Promise<GlobalConfig> => {
    const response = await fetch(`${API_BASE}/config/global`);
    return handleResponse(response);
  },

  updateGlobalConfig: async (config: GlobalConfig): Promise<GlobalConfig> => {
    const response = await fetch(`${API_BASE}/config/global`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    return handleResponse(response);
  },

  listSites: async (): Promise<SiteConfig[]> => {
    const response = await fetch(`${API_BASE}/config/sites`);
    return handleResponse(response);
  },

  getSite: async (siteId: string): Promise<SiteConfig> => {
    const response = await fetch(`${API_BASE}/config/sites/${siteId}`);
    return handleResponse(response);
  },

  createSite: async (site: SiteConfig): Promise<SiteConfig> => {
    const response = await fetch(`${API_BASE}/config/sites`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(site),
    });
    return handleResponse(response);
  },

  updateSite: async (siteId: string, site: SiteConfig): Promise<SiteConfig> => {
    const response = await fetch(`${API_BASE}/config/sites/${siteId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(site),
    });
    return handleResponse(response);
  },

  deleteSite: async (siteId: string): Promise<void> => {
    const response = await fetch(`${API_BASE}/config/sites/${siteId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Request failed');
    }
  },

  getSubscription: async (siteId: string, useCache = true): Promise<string> => {
    const response = await fetch(`${API_BASE}/subscriptions/${siteId}?use_cache=${useCache}`);
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Request failed');
    }
    return response.text();
  },

  fetchSubscription: async (siteId: string): Promise<FetchSummaryResponse> => {
    const response = await fetch(`${API_BASE}/subscriptions/${siteId}/fetch`, {
      method: 'POST',
    });
    return handleResponse(response);
  },
};
