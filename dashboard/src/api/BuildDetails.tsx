import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { TBuildDetails } from '@/types/tree/BuildDetails';

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
