import { useQuery, UseQueryResult } from '@tanstack/react-query';

import type { Tree } from '../types/tree/Tree';

import http from './api';

const fetchTreeCheckoutData = async (origin: string): Promise<Tree[]> => {
  const res = await http.get('/api/tree/', { params: { origin } });
  return res.data;
};

export const useTreeTable = (origin: string): UseQueryResult<Tree[]> => {
  return useQuery({
    queryKey: ['treeData', origin],
    queryFn: () => fetchTreeCheckoutData(origin),
  });
};
