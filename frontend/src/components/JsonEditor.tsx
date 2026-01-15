import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface JsonEditorProps<T> {
  value: T;
  onChange: (value: T) => void;
  onSave?: (value: T) => Promise<void>;
  height?: string;
  readOnly?: boolean;
}

export function JsonEditor<T>({ value, onChange, onSave, height = '400px', readOnly = false }: JsonEditorProps<T>) {
  const [jsonString, setJsonString] = useState(() => JSON.stringify(value, null, 2));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    setJsonString(JSON.stringify(value, null, 2));
  }, [value]);

  const handleChange = (newValue: string | undefined) => {
    if (!newValue) return;
    setJsonString(newValue);
    setError(null);
    setSaveSuccess(false);
    try {
      const parsed = JSON.parse(newValue);
      onChange(parsed);
    } catch {
      setError('Invalid JSON');
    }
  };

  const handleSave = async () => {
    if (!onSave || error) return;
    setSaving(true);
    try {
      const parsed = JSON.parse(jsonString);
      await onSave(parsed);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-2">
      <div className="border rounded-lg overflow-hidden">
        <Editor
          height={height}
          defaultLanguage="json"
          value={jsonString}
          onChange={handleChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            readOnly,
            tabSize: 2,
          }}
        />
      </div>
      <div className="flex items-center justify-between">
        <div>
          {error && <span className="text-red-600 text-sm">{error}</span>}
          {saveSuccess && <span className="text-green-600 text-sm">Saved successfully</span>}
        </div>
        {onSave && (
          <button
            onClick={handleSave}
            disabled={!!error || saving || readOnly}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        )}
      </div>
    </div>
  );
}
