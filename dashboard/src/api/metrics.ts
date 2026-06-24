import { useQuery, type UseQueryResult } from '@tanstack/react-query';

import type { MetricsResponse } from '@/types/metrics';

import { RequestData } from './commonRequest';

type FetchMetricsParams = {
  startDaysAgo: number;
  endDaysAgo: number;
};

export const fetchMetrics = async ({
  startDaysAgo,
  endDaysAgo,
}: FetchMetricsParams): Promise<MetricsResponse> => {
  const data = await RequestData.get<MetricsResponse>('/api/metrics/', {
    params: {
      start_days_ago: startDaysAgo,
      end_days_ago: endDaysAgo,
    },
  });

  return data;
};

export const useMetrics = ({
  startDaysAgo,
  endDaysAgo,
}: FetchMetricsParams): UseQueryResult<MetricsResponse> => {
  return useQuery({
    queryKey: ['metrics', startDaysAgo, endDaysAgo],
    queryFn: () => fetchMetrics({ startDaysAgo, endDaysAgo }),
  });
};
