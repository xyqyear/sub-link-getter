import { useState } from 'react';
import Form from '@rjsf/core';
import type { RJSFSchema, UiSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';
import type { SiteConfig } from '../types';

interface SiteFormProps {
  schema: RJSFSchema;
  initialData?: SiteConfig;
  onSubmit: (data: SiteConfig) => Promise<void>;
  isNew?: boolean;
}

const uiSchema: UiSchema = {
  password: {
    'ui:widget': 'password',
  },
  openrouter_api_key: {
    'ui:widget': 'password',
  },
  product_url: {
    'ui:placeholder': 'https://example.com/product',
  },
  subscription_name_pattern: {
    'ui:placeholder': '.*',
  },
  'ui:order': [
    'id',
    'name',
    'product_url',
    'username',
    'password',
    'login_wait_selector',
    'post_login_wait_selector',
    'username_selector',
    'password_selector',
    'login_button_selector',
    'captcha_image_selector',
    'captcha_input_selector',
    'captcha_retry_count',
    'subscription_label_selector',
    'subscription_group_selector',
    'subscription_url_type',
    'subscription_url_selector',
    'subscription_url_attribute',
    'subscription_name_pattern',
    'subscription_url_retry_count',
    'subscription_url_retry_delay_ms',
    'content_validation',
  ],
};

export function SiteForm({ schema, initialData, onSubmit, isNew }: SiteFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const modifiedSchema = { ...schema };
  if (!isNew && modifiedSchema.properties) {
    modifiedSchema.properties = {
      ...modifiedSchema.properties,
      id: { ...modifiedSchema.properties.id as object, readOnly: true },
    };
  }

  const handleSubmit = async (data: { formData?: unknown }) => {
    if (!data.formData) return;
    setLoading(true);
    setError(null);
    try {
      await onSubmit(data.formData as SiteConfig);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      <Form
        schema={modifiedSchema}
        uiSchema={uiSchema}
        validator={validator}
        formData={initialData}
        onSubmit={handleSubmit}
        disabled={loading}
        className="rjsf-form"
      >
        <div className="mt-4">
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : isNew ? 'Create Site' : 'Update Site'}
          </button>
        </div>
      </Form>
    </div>
  );
}
