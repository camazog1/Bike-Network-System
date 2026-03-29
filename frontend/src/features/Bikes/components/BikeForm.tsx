import { useState } from 'react';
import type { FormEvent } from 'react';
import type { BikePayload } from '../types';
import type { ApiError } from '../../../types';

interface BikeFormProps {
  defaultValues?: Partial<BikePayload>;
  onSubmit: (payload: BikePayload) => void;
  isPending: boolean;
  error?: ApiError | null;
}

export default function BikeForm({ defaultValues, onSubmit, isPending, error }: BikeFormProps) {
  const [name, setName] = useState(defaultValues?.name ?? '');
  const [brand, setBrand] = useState(defaultValues?.brand ?? '');
  const [type, setType] = useState(defaultValues?.type ?? '');
  const [status, setStatus] = useState(defaultValues?.status ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!name.trim()) errors.name = 'Name is required';
    if (!brand.trim()) errors.brand = 'Brand is required';
    if (!type.trim()) errors.type = 'Type is required';
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    const payload: BikePayload = { name: name.trim(), brand: brand.trim(), type: type.trim() };
    if (status.trim()) payload.status = status.trim();
    onSubmit(payload);
  }

  function getApiFieldError(field: string): string | undefined {
    if (error?.error === 'VALIDATION_ERROR' && error.details) {
      return error.details.find((d) => d.toLowerCase().includes(field.toLowerCase()));
    }
    return undefined;
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-lg text-left">
      {error && error.error !== 'VALIDATION_ERROR' && (
        <div className="text-danger-400 text-sm p-2 border border-danger-400 rounded">
          {error.message ?? 'An error occurred'}
        </div>
      )}

      <label>
        <div className="text-sm font-medium text-text mb-1">Name *</div>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.name || getApiFieldError('name')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.name || getApiFieldError('name')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Brand *</div>
        <input
          type="text"
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.brand || getApiFieldError('brand')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.brand || getApiFieldError('brand')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Type *</div>
        <input
          type="text"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.type || getApiFieldError('type')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.type || getApiFieldError('type')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Status</div>
        <input
          type="text"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          placeholder="e.g. available, in-use, maintenance"
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
      </label>

      <button
        type="submit"
        disabled={isPending}
        className={`px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 self-start ${isPending ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {isPending ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
