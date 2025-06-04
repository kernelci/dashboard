import { useQuery, type UseQueryResult } from '@tanstack/react-query';

import { MILLISECONDS_IN_ONE_HOUR } from '@/utils/date';

import type { OriginsResponse } from '@/types/origins';

import { RequestData } from './commonRequest';

const fetchOrigins = async (): Promise<OriginsResponse> => {
  const data = await RequestData.get<OriginsResponse>('/api/origins/');
  return data;
};

const ORIGIN_CACHE_DURATION = 2 * MILLISECONDS_IN_ONE_HOUR;

export const useOrigins = (): UseQueryResult<OriginsResponse> => {
  return useQuery({
    queryKey: ['origins'],
    queryFn: () => fetchOrigins(),
    refetchOnWindowFocus: false,
    staleTime: ORIGIN_CACHE_DURATION,
  });
};
