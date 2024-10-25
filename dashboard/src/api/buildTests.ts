import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { TestHistory } from '@/types/general';

import http from './api';

const fetchBuildTestsData = async (buildId: string): Promise<TestHistory[]> => {
  const res = await http.get(`/api/build/${buildId}/tests`);

  return res.data;
};

export const useBuildTests = (
  buildId: string,
): UseQueryResult<TestHistory[]> => {
  return useQuery({
    queryKey: ['buildTests', buildId],
    queryFn: () => fetchBuildTestsData(buildId),
  });
};
