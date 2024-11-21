import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TBuildDetails } from '@/types/tree/BuildDetails';

import type { TIssue } from '@/types/general';

import http from './api';

const fetchTreeDetailData = async (buildId: string): Promise<TBuildDetails> => {
  const res = await http.get(`/api/build/${buildId}`);

  const { _timestamp, ...data } = res.data;
  data.timestamp = _timestamp;
  return data;
};

export const useBuildDetails = (
  buildId: string,
): UseQueryResult<TBuildDetails> => {
  return useQuery({
    queryKey: ['treeData', buildId],
    queryFn: () => fetchTreeDetailData(buildId),
  });
};

const fetchBuildIssues = async (buildId: string): Promise<TIssue[]> => {
  const res = await http.get<TIssue[]>(`/api/build/${buildId}/issues`);
  return res.data;
};

export const useBuildIssues = (buildId: string): UseQueryResult<TIssue[]> => {
  return useQuery({
    queryKey: ['buildIssues', buildId],
    queryFn: () => fetchBuildIssues(buildId),
  });
};
