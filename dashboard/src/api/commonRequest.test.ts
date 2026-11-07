import type { AxiosRequestConfig } from 'axios';
import { describe, expect, it } from 'vitest';

import { getMissingTreeResource } from '@/utils/treeDetails';
import { retryHandler } from '@/utils/query';

import { ApiError, RequestData } from './commonRequest';

const responseConfig = (data: unknown): AxiosRequestConfig => ({
  adapter: async config => ({
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  }),
});

describe.each(['get', 'post'] as const)('RequestData.%s', method => {
  const request = (data: unknown): Promise<unknown> =>
    method === 'get'
      ? RequestData.get('/tree/hash/summary', responseConfig(data))
      : RequestData.post('/tree/hash/summary', {}, responseConfig(data));

  it.each(['tree', 'branch', 'commit'])(
    'preserves a missing %s in an HTTP 200 error without retrying',
    async resource => {
      const body = { error: `${resource} not found.`, resource };
      const error: unknown = await request(body).catch(
        (caught: unknown) => caught,
      );

      expect(error).toBeInstanceOf(ApiError);
      if (!(error instanceof ApiError)) {
        throw new Error('Expected an API error');
      }
      expect(error.message).toBe(`200:${body.error}`);
      expect(error.data).toEqual(body);
      expect(getMissingTreeResource(error)).toBe(resource);
      expect(retryHandler()(0, error)).toBe(false);
    },
  );

  it.each([
    { error: 'No results available for this tree/branch/commit' },
    { error: 'Unexpected error', resource: 'invalid' },
  ])('keeps other API errors separate from missing checkouts', async body => {
    const error: unknown = await request(body).catch(
      (caught: unknown) => caught,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect(getMissingTreeResource(error)).toBeUndefined();
  });

  it('returns successful data unchanged', async () => {
    const data = { summary: { builds: { status: { PASS: 1 } } } };
    await expect(request(data)).resolves.toEqual(data);
  });
});
