import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { Tree, TreeFastPathResponse } from '@/types/tree/Tree';

import http from './api';

const fetchTreeCheckoutData = async (
  origin: string,
  time?: number,
): Promise<Tree[]> => {
  const res = await http.get('/api/tree/', { params: { origin, time } });
  return res.data;
};

export const useTreeTable = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<Tree[]> => {
  const { origin, time } = useSearch({ from: '/tree' });

  const queryKey = ['treeTable', origin, time];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeCheckoutData(origin, time),
    enabled,
  });
};

const fetchTreeFastCheckoutData = async (
  origin: string,
  time?: number,
): Promise<TreeFastPathResponse> => {
  const res = await http.get('/api/tree-fast/', { params: { origin, time } });
  return res.data;
};

export const useTreeTableFast = (): UseQueryResult<TreeFastPathResponse> => {
  const { origin, time } = useSearch({ from: '/tree' });

  const queryKey = ['treeTableFast', origin, time];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeFastCheckoutData(origin, time),
  });
};
