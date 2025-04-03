import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  Tree,
  TreeFastPathResponse,
  TreeLatestResponse,
} from '@/types/tree/Tree';
import { DEFAULT_ORIGIN } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchTreeCheckoutData = async (
  origin: string,
  intervalInDays?: number,
): Promise<Tree[]> => {
  const data = await RequestData.get<Tree[]>('/api/tree/', {
    params: { origin, intervalInDays },
  });
  return data;
};

export const useTreeTable = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<Tree[]> => {
  const { origin, intervalInDays } = useSearch({ from: '/_main/tree' });

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
  const data = await RequestData.get<TreeFastPathResponse>('/api/tree-fast/', {
    params: { origin, intervalInDays },
  });
  return data;
};

export const useTreeTableFast = (): UseQueryResult<TreeFastPathResponse> => {
  const { origin, intervalInDays } = useSearch({ from: '/_main/tree' });

  const queryKey = ['treeTableFast', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeFastCheckoutData(origin, intervalInDays),
  });
};

const fetchTreeLatest = async (
  treeName: string,
  branch: string,
  origin?: string,
): Promise<TreeLatestResponse> => {
  const data = await RequestData.get<TreeLatestResponse>(
    `/api/tree/${treeName}/${branch}`,
    {
      params: { origin: origin || DEFAULT_ORIGIN },
    },
  );
  return data;
};

export const useTreeLatest = (
  treeName: string,
  branch: string,
  origin?: string,
): UseQueryResult<TreeLatestResponse> => {
  return useQuery({
    queryKey: ['treeLatest', treeName, branch, origin],
    queryFn: () => fetchTreeLatest(treeName, branch, origin),
  });
};
