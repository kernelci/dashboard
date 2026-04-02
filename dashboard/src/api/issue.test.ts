import { describe, it, expect, vi, beforeEach } from 'vitest';

import { fetchIssueListing } from './issue';

const mockGet = vi.fn();

vi.mock('./commonRequest', () => ({
  RequestData: {
    get: (...args: unknown[]): unknown => mockGet(...args),
  },
}));

vi.mock('@/utils/utils', () => ({
  mapFiltersKeysToBackendCompatible: (
    filters: Record<string, unknown>,
  ): Record<string, string[]> =>
    Object.fromEntries(
      Object.entries(filters).map(([k, v]) => [`filter_${k}`, [String(v)]]),
    ),
}));

const MOCK_RESPONSE = {
  issues: [],
  extras: {},
  filters: { origins: [], culprits: [], categories: [] },
};

describe('fetchIssueListing', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue(MOCK_RESPONSE);
  });

  it('calls /api/issue/ with startTimestampInSeconds and endTimestampInSeconds', async () => {
    const startTimestampInSeconds = 1_700_000_000;
    const endTimestampInSeconds = 1_700_432_000;

    await fetchIssueListing({
      startTimestampInSeconds,
      endTimestampInSeconds,
      filters: {},
    });

    expect(mockGet).toHaveBeenCalledWith('/api/issue/', {
      params: { startTimestampInSeconds, endTimestampInSeconds },
    });
  });

  it('includes backend-compatible filter params alongside timestamps', async () => {
    const startTimestampInSeconds = 1_700_000_000;
    const endTimestampInSeconds = 1_700_432_000;

    await fetchIssueListing({
      startTimestampInSeconds,
      endTimestampInSeconds,
      filters: { origin: 'maestro' },
    });

    expect(mockGet).toHaveBeenCalledWith('/api/issue/', {
      params: {
        startTimestampInSeconds,
        endTimestampInSeconds,
        filter_origin: ['maestro'],
      },
    });
  });

  it('returns the API response', async () => {
    const result = await fetchIssueListing({
      startTimestampInSeconds: 1_700_000_000,
      endTimestampInSeconds: 1_700_432_000,
      filters: {},
    });

    expect(result).toEqual(MOCK_RESPONSE);
  });

  it('propagates errors thrown by RequestData.get', async () => {
    mockGet.mockRejectedValue(new Error('network error'));

    await expect(
      fetchIssueListing({
        startTimestampInSeconds: 1_700_000_000,
        endTimestampInSeconds: 1_700_432_000,
        filters: {},
      }),
    ).rejects.toThrow('network error');
  });
});
