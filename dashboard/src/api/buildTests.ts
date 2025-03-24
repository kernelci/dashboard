import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TestHistory } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchBuildTestsData = async (buildId: string): Promise<TestHistory[]> => {
  const data = await RequestData.get<TestHistory[]>(
    `/api/build/${buildId}/tests`,
  );

  return data;
};

export const useBuildTests = (
  buildId: string,
): UseQueryResult<TestHistory[]> => {
  return useQuery({
    queryKey: ['buildTests', buildId],
    queryFn: () => fetchBuildTestsData(buildId),
    refetchOnWindowFocus: false,
  });
};
