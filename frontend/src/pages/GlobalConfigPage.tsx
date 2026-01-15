import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Form from '@rjsf/core';
import type { RJSFSchema, UiSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';
import type { GlobalConfig } from '../types';
import { api } from '../api';

const uiSchema: UiSchema = {
  openrouter_api_key: {
    'ui:widget': 'password',
  },
};

export function GlobalConfigPage() {
  const [schema, setSchema] = useState<RJSFSchema | null>(null);
  const [config, setConfig] = useState<GlobalConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [schemaData, configData] = await Promise.all([
          api.getGlobalSchema(),
          api.getGlobalConfig(),
        ]);
        setSchema(schemaData as RJSFSchema);
        setConfig(configData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSubmit = async (data: { formData?: unknown }) => {
    if (!data.formData) return;
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const updated = await api.updateGlobalConfig(data.formData as GlobalConfig);
      setConfig(updated);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error && !schema) {
    return (
      <div className="space-y-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
        <Link to="/" className="text-blue-600 hover:underline">Back to sites</Link>
      </div>
    );
  }

  if (!schema || !config) {
    return <div>Config not available</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/" className="text-gray-500 hover:text-gray-700">&larr; Back</Link>
        <h1 className="text-2xl font-bold">Global Configuration</h1>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          Saved successfully
        </div>
      )}

      <Form
        schema={schema}
        uiSchema={uiSchema}
        validator={validator}
        formData={config}
        onSubmit={handleSubmit}
        disabled={saving}
        className="rjsf-form"
      >
        <div className="mt-4">
          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </Form>
    </div>
  );
}
