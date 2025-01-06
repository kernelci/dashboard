import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  Tree,
  TreeFastPathResponse,
  TreeLatestResponse,
} from '@/types/tree/Tree';
import { DEFAULT_ORIGIN, type TOrigins } from '@/types/general';

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

const fetchTreeLatest = async (
  treeName: string,
  branch: string,
  origin?: TOrigins,
): Promise<TreeLatestResponse> => {
  const res = await http.get(`/api/tree/${treeName}/${branch}`, {
    params: { origin: origin || DEFAULT_ORIGIN },
  });
  return res.data;
};

export const useTreeLatest = (
  treeName: string,
  branch: string,
  origin?: TOrigins,
): UseQueryResult<TreeLatestResponse> => {
  return useQuery({
    queryKey: ['treeLatest', treeName, branch, origin],
    queryFn: () => fetchTreeLatest(treeName, branch, origin),
  });
};
