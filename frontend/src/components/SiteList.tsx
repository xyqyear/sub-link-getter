import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { SiteConfig } from '../types';
import { api } from '../api';

interface SiteListProps {
  sites: SiteConfig[];
  onRefresh: () => void;
}

export function SiteList({ sites, onRefresh }: SiteListProps) {
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFetch = async (siteId: string) => {
    setLoading((prev) => ({ ...prev, [siteId]: true }));
    setError(null);
    setSuccess(null);
    try {
      const result = await api.fetchSubscription(siteId);
      setSuccess(`Fetched ${result.name}: ${result.content_length} bytes`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setLoading((prev) => ({ ...prev, [siteId]: false }));
    }
  };

  const handleDelete = async (siteId: string) => {
    if (!confirm(`Delete site "${siteId}"?`)) return;
    try {
      await api.deleteSite(siteId);
      onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  const getSubscriptionUrl = (siteId: string) => {
    return `${window.location.origin}/api/subscriptions/${siteId}`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard');
    setTimeout(() => setSuccess(null), 2000);
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {sites.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No sites configured. <Link to="/sites/new" className="text-blue-600 hover:underline">Add one</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {sites.map((site) => (
            <div
              key={site.id}
              className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{site.name}</h3>
                  <p className="text-sm text-gray-500">{site.id}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded flex-1 truncate">
                      {getSubscriptionUrl(site.id)}
                    </code>
                    <button
                      onClick={() => copyToClipboard(getSubscriptionUrl(site.id))}
                      className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded"
                    >
                      Copy
                    </button>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleFetch(site.id)}
                    disabled={loading[site.id]}
                    className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
                  >
                    {loading[site.id] ? 'Fetching...' : 'Refresh'}
                  </button>
                  <Link
                    to={`/sites/${site.id}`}
                    className="px-3 py-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={() => handleDelete(site.id)}
                    className="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
