import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  TTreeDetailsFilter,
  BuildCountsResponse,
  TreeDetailsFullData,
  LogFilesResponse,
  TreeDetailsSummary,
  TreeDetailsBoots,
  TreeDetailsBuilds,
  TreeDetailsTests,
} from '@/types/tree/TreeDetails';

import { getTargetFilter, type TFilter } from '@/types/general';

import { mapFiltersKeysToBackendCompatible } from '@/utils/utils';

import http from './api';

type TreeSearchParameters = {
  origin: string;
  gitUrl?: string;
  gitBranch?: string;
};

const useTreeSearchParameters = (): TreeSearchParameters => {
  const {
    origin,
    treeInfo: { gitUrl, gitBranch },
  } = useSearch({ from: '/tree/$treeId' });

  return { origin, gitUrl, gitBranch };
};

type TreeDetailsVariants = 'full' | 'builds' | 'boots' | 'tests' | 'summary';

type TreeDetailsResponseTable = {
  full: TreeDetailsFullData;
  summary: TreeDetailsSummary;
  builds: TreeDetailsBuilds;
  boots: TreeDetailsBoots;
  tests: TreeDetailsTests;
};

const fetchTreeDetails = async ({
  treeId,
  treeSearchParameters,
  filter = {},
  variant,
}: {
  treeId: string;
  treeSearchParameters: TreeSearchParameters;
  filter: TTreeDetailsFilter;
  variant: TreeDetailsVariants;
}): Promise<TreeDetailsFullData> => {
  const backendCompatibleFilters = mapFiltersKeysToBackendCompatible(filter);

  const params = {
    git_branch: treeSearchParameters.gitBranch,
    git_url: treeSearchParameters.gitUrl,
    origin: treeSearchParameters.origin,
    ...backendCompatibleFilters,
  };

  const urlTable: Record<TreeDetailsVariants, string> = {
    full: `/api/tree/${treeId}/full`,
    builds: `/api/tree/${treeId}/builds`,
    boots: `/api/tree/${treeId}/boots`,
    tests: `/api/tree/${treeId}/tests`,
    summary: `/api/tree/${treeId}/summary`,
  };
  const res = await http.get<TreeDetailsFullData>(urlTable[variant], {
    params: params,
  });

  return res.data;
};

type TreeDetailsResponse<T extends keyof TreeDetailsResponseTable> =
  TreeDetailsResponseTable[T];

export type UseTreeDetailsWithoutVariant = {
  treeId: string;
  filter?: TFilter;
  enabled?: boolean;
};

type UseTreeDetailsParameters<T extends TreeDetailsVariants> = {
  variant: T;
} & UseTreeDetailsWithoutVariant;

export const useTreeDetails = <T extends TreeDetailsVariants>({
  treeId,
  filter = {},
  enabled = true,
  variant,
}: UseTreeDetailsParameters<T>): UseQueryResult<TreeDetailsResponse<T>> => {
  const testFilter = getTargetFilter(filter, 'test');
  const treeDetailsFilter = getTargetFilter(filter, 'treeDetails');
  const treeSearchParameters = useTreeSearchParameters();

  return useQuery({
    queryKey: [
      'treeTests',
      treeId,
      treeSearchParameters,
      testFilter,
      treeDetailsFilter,
      variant,
    ],
    queryFn: () =>
      fetchTreeDetails({
        treeId,
        treeSearchParameters,
        variant,
        filter: {
          ...testFilter,
          ...treeDetailsFilter,
        },
      }),
    enabled,
    placeholderData: previousData => previousData,
  });
};

const fetchLogFiles = async (logUrl: string): Promise<BuildCountsResponse> => {
  const res = await http.get<BuildCountsResponse>(`/api/log-downloader/`, {
    params: {
      log_download_url: logUrl,
    },
  });
  return res.data;
};

type Config = {
  enabled?: boolean;
};

export const useLogFiles = (
  {
    logUrl,
  }: {
    logUrl: string;
  },
  { enabled }: Config = { enabled: true },
): UseQueryResult<LogFilesResponse> => {
  return useQuery({
    queryKey: [logUrl],
    enabled,
    retry: 1,
    queryFn: () => fetchLogFiles(logUrl),
  });
};
