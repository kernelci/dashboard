import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { Tree, TreeFastPathResponse } from '@/types/tree/Tree';

import http from './api';

const fetchTreeCheckoutData = async (
  origin: string,
  intervalInDays?: number,
): Promise<Tree[]> => {
  const res = await http.get('/api/tree/', {
    params: { origin, intervalInDays },
  });
  return res.data;
};

export const useTreeTable = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<Tree[]> => {
  const { origin, intervalInDays } = useSearch({ from: '/tree' });

  const queryKey = ['treeTable', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeCheckoutData(origin, intervalInDays),
    enabled,
  });
};

const fetchTreeFastCheckoutData = async (
  origin: string,
  intervalInDays?: number,
): Promise<TreeFastPathResponse> => {
  const res = await http.get('/api/tree-fast/', {
    params: { origin, intervalInDays },
  });
  return res.data;
};

export const useTreeTableFast = (): UseQueryResult<TreeFastPathResponse> => {
  const { origin, intervalInDays } = useSearch({ from: '/tree' });

  const queryKey = ['treeTableFast', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeFastCheckoutData(origin, intervalInDays),
  });
};
