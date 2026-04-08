import { describe, it, expect, vi, beforeEach } from 'vitest';

import { fetchIssueListing } from './issue';

// Arbitrary round-number timestamps ~5 days apart, no domain significance.
// Chosen for readability; any two valid timestamps where start < end would work.
//   2023-11-14 22:13:20 UTC
const START_TIMESTAMP_SECONDS = 1_700_000_000;
const END_TIMESTAMP_SECONDS = 1_700_432_000; // 5 days later

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
  const startTimestampInSeconds = START_TIMESTAMP_SECONDS;
  const endTimestampInSeconds = END_TIMESTAMP_SECONDS;

  beforeEach(() => {
    mockGet.mockResolvedValue(MOCK_RESPONSE);
  });

  it('calls /api/issue/ with startTimestampInSeconds and endTimestampInSeconds', async () => {
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
      startTimestampInSeconds,
      endTimestampInSeconds,
      filters: {},
    });

    expect(result).toEqual(MOCK_RESPONSE);
  });

  it('propagates errors thrown by RequestData.get', async () => {
    mockGet.mockRejectedValue(new Error('network error'));

    expect(
      fetchIssueListing({
        startTimestampInSeconds,
        endTimestampInSeconds,
        filters: {},
      }),
    ).rejects.toThrow('network error');
  });
});
