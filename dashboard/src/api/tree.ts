import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  Tree,
  TreeFastPathResponse,
  TreeLatestResponse,
  TreeV2,
} from '@/types/tree/Tree';
import { DEFAULT_ORIGIN } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchTreeCheckoutData = async (
  origin: string,
  intervalInDays?: number,
): Promise<Tree[]> => {
  const params = {
    origin: origin,
    interval_in_days: intervalInDays,
  };

  const data = await RequestData.get<Tree[]>('/api/tree/', {
    params,
  });
  return data;
};

export const useTreeTable = ({
  enabled,
}: {
  enabled: boolean;
}): UseQueryResult<Tree[]> => {
  const { origin, intervalInDays } = useSearch({ from: '/_main/tree/v1' });

  const queryKey = ['treeTable', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeCheckoutData(origin, intervalInDays),
    enabled,
    refetchOnWindowFocus: false,
  });
};

const fetchTreeFastCheckoutData = async (
  origin: string,
  intervalInDays?: number,
): Promise<TreeFastPathResponse> => {
  const params = {
    origin: origin,
    interval_in_days: intervalInDays,
  };

  const data = await RequestData.get<TreeFastPathResponse>('/api/tree-fast/', {
    params,
  });
  return data;
};

export const useTreeTableFast = (): UseQueryResult<TreeFastPathResponse> => {
  const { origin, intervalInDays } = useSearch({ from: '/_main/tree/v1' });

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
  gitCommitHash?: string,
): Promise<TreeLatestResponse> => {
  const data = await RequestData.get<TreeLatestResponse>(
    `/api/tree/${treeName}/${branch}`,
    {
      params: {
        origin: origin || DEFAULT_ORIGIN,
        commit_hash: gitCommitHash,
      },
    },
  );
  return data;
};

export const useTreeLatest = (
  treeName: string,
  branch: string,
  origin?: string,
  gitCommitHash?: string,
): UseQueryResult<TreeLatestResponse> => {
  return useQuery({
    queryKey: ['treeLatest', treeName, branch, origin, gitCommitHash],
    queryFn: () => fetchTreeLatest(treeName, branch, origin, gitCommitHash),
    refetchOnWindowFocus: false,
  });
};

const fetchTreeListingV2 = async (
  origin: string,
  intervalInDays?: number,
): Promise<TreeV2[]> => {
  const params = {
    origin: origin,
    interval_in_days: intervalInDays,
  };

  const data = await RequestData.get<TreeV2[]>('/api/tree-v2/', {
    params,
  });
  return data;
};

export const useTreeListingV2 = (): UseQueryResult<TreeV2[]> => {
  const { origin, intervalInDays } = useSearch({ from: '/_main/tree' });

  const queryKey = ['treeTableV2', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeListingV2(origin, intervalInDays),
    refetchOnWindowFocus: false,
  });
};
