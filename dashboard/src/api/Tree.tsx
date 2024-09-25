import { useQuery, UseQueryResult } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { Tree, TreeFastPathResponse } from '@/types/tree/Tree';

import http from './api';

const fetchTreeCheckoutData = async (origin: string): Promise<Tree[]> => {
  const res = await http.get('/api/tree/', { params: { origin } });
  return res.data;
};

export const useTreeTable = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<Tree[]> => {
  const { origin } = useSearch({ from: '/tree' });

  return useQuery({
    queryKey: ['treeTable', origin],
    queryFn: () => fetchTreeCheckoutData(origin),
    enabled,
  });
};

const fetchTreeFastCheckoutData = async (
  origin: string,
): Promise<TreeFastPathResponse> => {
  const res = await http.get('/api/tree-fast/', { params: { origin } });
  return res.data;
};

export const useTreeTableFast = (): UseQueryResult<TreeFastPathResponse> => {
  const { origin } = useSearch({ from: '/tree' });
  return useQuery({
    queryKey: ['treeTableFAst', origin],
    queryFn: () => fetchTreeFastCheckoutData(origin),
  });
};
