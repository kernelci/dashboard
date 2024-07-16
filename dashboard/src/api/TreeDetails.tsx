import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { TreeDetails } from '@/types/tree/TreeDetails';

import http from './api';

const fetchTreeDetailData = async (treeId: string): Promise<TreeDetails> => {
  const res = await http.get(`/api/tree/${treeId}`);
  return res.data;
};

export const useTreeDetails = (treeId: string): UseQueryResult<TreeDetails> => {
  return useQuery({
    queryKey: ['treeData', treeId],
    queryFn: () => fetchTreeDetailData(treeId),
  });
};
