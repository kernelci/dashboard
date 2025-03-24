import type { UseBaseQueryOptions } from '@tanstack/react-query';

export type ApiUseQueryOptions<T> = Omit<
  Partial<UseBaseQueryOptions<T>>,
  'queryKey' | 'queryFn'
>;
