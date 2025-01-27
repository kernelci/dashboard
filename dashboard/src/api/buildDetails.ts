import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TBuildDetails } from '@/types/tree/BuildDetails';

import type { TIssue } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchBuildDetailsData = async (
  buildId: string,
): Promise<TBuildDetails> => {
  const res = await RequestData.get<TBuildDetails & { _timestamp: string }>(
    `/api/build/${buildId}`,
  );

  const { _timestamp, ...data } = res;
  data.timestamp = _timestamp;
  return data;
};

export const useBuildDetails = (
  buildId: string,
): UseQueryResult<TBuildDetails> => {
  return useQuery({
    queryKey: ['treeData', buildId],
    queryFn: () => fetchBuildDetailsData(buildId),
  });
};

const fetchBuildIssues = async (buildId: string): Promise<TIssue[]> => {
  const data = await RequestData.get<TIssue[]>(`/api/build/${buildId}/issues`);

  return data;
};

export const useBuildIssues = (buildId: string): UseQueryResult<TIssue[]> => {
  return useQuery({
    queryKey: ['buildIssues', buildId],
    queryFn: () => fetchBuildIssues(buildId),
    enabled: buildId !== '',
  });
};
