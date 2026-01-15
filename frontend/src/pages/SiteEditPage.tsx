import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import type { RJSFSchema } from '@rjsf/utils';
import { SiteForm } from '../components/SiteForm';
import { JsonEditor } from '../components/JsonEditor';
import type { SiteConfig } from '../types';
import { api } from '../api';

type EditorMode = 'form' | 'json';

export function SiteEditPage() {
  const { siteId } = useParams<{ siteId: string }>();
  const navigate = useNavigate();
  const isNew = siteId === 'new';

  const [schema, setSchema] = useState<RJSFSchema | null>(null);
  const [site, setSite] = useState<SiteConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<EditorMode>('form');

  useEffect(() => {
    const load = async () => {
      try {
        const schemaData = await api.getSchema();
        setSchema(schemaData as RJSFSchema);

        if (!isNew && siteId) {
          const siteData = await api.getSite(siteId);
          setSite(siteData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [siteId, isNew]);

  const handleSubmit = async (data: SiteConfig) => {
    if (isNew) {
      await api.createSite(data);
    } else if (siteId) {
      await api.updateSite(siteId, data);
    }
    navigate('/');
  };

  const handleJsonSave = async (data: SiteConfig) => {
    await handleSubmit(data);
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

  if (!schema) {
    return <div>Schema not available</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-gray-500 hover:text-gray-700">&larr; Back</Link>
          <h1 className="text-2xl font-bold">
            {isNew ? 'New Site' : `Edit: ${site?.name || siteId}`}
          </h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setMode('form')}
            className={`px-3 py-1.5 rounded ${mode === 'form' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            Form
          </button>
          <button
            onClick={() => setMode('json')}
            className={`px-3 py-1.5 rounded ${mode === 'json' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            JSON
          </button>
        </div>
      </div>

      {mode === 'form' ? (
        <SiteForm
          schema={schema}
          initialData={site || undefined}
          onSubmit={handleSubmit}
          isNew={isNew}
        />
      ) : (
        <JsonEditor
          value={site || ({} as Partial<SiteConfig>)}
          onChange={(data) => setSite(data as SiteConfig)}
          onSave={(data) => handleJsonSave(data as SiteConfig)}
          height="600px"
        />
      )}
    </div>
  );
}
