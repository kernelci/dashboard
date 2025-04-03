import { useQuery, type UseQueryResult } from '@tanstack/react-query';

import { MILLISECONDS_IN_ONE_HOUR } from '@/utils/date';

import { RequestData } from './commonRequest';

const fetchOrigins = async (): Promise<string[]> => {
  const data = await RequestData.get<string[]>('/api/origins/');
  return data;
};

const ORIGIN_CACHE_DURATION = 2 * MILLISECONDS_IN_ONE_HOUR;

export const useOrigins = (): UseQueryResult<string[]> => {
  return useQuery({
    queryKey: ['origins'],
    queryFn: () => fetchOrigins(),
    refetchOnWindowFocus: false,
    staleTime: ORIGIN_CACHE_DURATION,
  });
};
