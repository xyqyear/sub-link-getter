import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { JsonEditor } from '../components/JsonEditor';
import type { GlobalConfig } from '../types';
import { api } from '../api';

export function GlobalConfigPage() {
  const [config, setConfig] = useState<GlobalConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getGlobalConfig();
        setConfig(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSave = async (data: GlobalConfig) => {
    await api.updateGlobalConfig(data);
    setConfig(data);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
        <Link to="/" className="text-blue-600 hover:underline">Back to sites</Link>
      </div>
    );
  }

  if (!config) {
    return <div>Config not available</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/" className="text-gray-500 hover:text-gray-700">&larr; Back</Link>
        <h1 className="text-2xl font-bold">Global Configuration</h1>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded text-sm">
        <strong>Note:</strong> The API key is sensitive. Make sure to keep it secure.
      </div>

      <JsonEditor
        value={config}
        onChange={setConfig}
        onSave={handleSave}
        height="400px"
      />

      <div className="text-sm text-gray-500 space-y-1">
        <p><strong>openrouter_api_key:</strong> API key for captcha recognition</p>
        <p><strong>headless:</strong> Run browser in headless mode</p>
        <p><strong>solve_cloudflare:</strong> Attempt to solve Cloudflare challenges</p>
        <p><strong>timeout:</strong> Browser operation timeout in milliseconds</p>
        <p><strong>cache_file:</strong> Path to cache file</p>
        <p><strong>browser_data_dir:</strong> Directory for browser data persistence</p>
      </div>
    </div>
  );
}
