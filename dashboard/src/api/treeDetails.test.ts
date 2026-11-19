import type { QueryObserverOptions } from '@tanstack/react-query';
import { QueryClient, QueryObserver } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';

import { sameCheckoutPlaceholder } from './treeDetails';

const options = (
  commit: string,
  queryFn: () => Promise<string>,
  testFilter = {},
): QueryObserverOptions<string> => {
  const queryKey = [
    'treeTests',
    'stable',
    'linux-6.1.y',
    commit,
    { origin: 'maestro' },
    testFilter,
    {},
    'summary',
    '/_main/tree/$treeName/$branch/$hash',
  ];
  return {
    queryKey,
    queryFn,
    placeholderData: sameCheckoutPlaceholder(queryKey),
  };
};

const pending = (): Promise<string> => new Promise(() => {});

describe('sameCheckoutPlaceholder', () => {
  it('keeps data for a filter change, not for a commit after an empty one', async () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const observer = new QueryObserver(
      client,
      options('aaaa', async () => 'aaaa'),
    );
    const unsubscribe = observer.subscribe(() => {});
    await vi.waitFor(() =>
      expect(observer.getCurrentResult().data).toBe('aaaa'),
    );

    observer.setOptions(options('aaaa', pending, { 'build.status': ['FAIL'] }));
    expect(observer.getCurrentResult().data).toBe('aaaa');

    observer.setOptions(
      options('bbbb', () => Promise.reject(new Error('No results'))),
    );
    await vi.waitFor(() =>
      expect(observer.getCurrentResult().status).toBe('error'),
    );

    observer.setOptions(options('cccc', pending));
    expect(observer.getCurrentResult().data).toBeUndefined();
    unsubscribe();
  });
});
