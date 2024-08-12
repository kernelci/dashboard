import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { TPathTests } from '@/types/general';

import http from './api';

const fetchBuildTestsData = async (
  buildId: string,
  path: string,
): Promise<TPathTests[]> => {
  const params = path ? { path } : {};
  const res = await http.get(`/api/build/${buildId}/tests`, { params });

  return res.data;
};

export const useBuildTests = (
  buildId: string,
  path = '',
): UseQueryResult<TPathTests[]> => {
  return useQuery({
    queryKey: ['buildTests', buildId, path],
    queryFn: () => fetchBuildTestsData(buildId, path),
  });
};
