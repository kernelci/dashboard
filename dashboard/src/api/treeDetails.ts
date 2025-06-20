import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import { treeDetailsDirectRouteName } from '@/types/tree/TreeDetails';
import type {
  TTreeDetailsFilter,
  BuildCountsResponse,
  TreeDetailsFullData,
  LogFilesResponse,
  TreeDetailsSummary,
  TreeDetailsBoots,
  TreeDetailsBuilds,
  TreeDetailsTests,
  TreeDetailsRouteFrom,
} from '@/types/tree/TreeDetails';

import { getTargetFilter, type TFilter } from '@/types/general';

import { mapFiltersKeysToBackendCompatible } from '@/utils/utils';

import { retryHandler } from '@/utils/query';

import { RequestData } from './commonRequest';

type TreeSearchParameters = {
  origin: string;
  gitUrl?: string;
  gitBranch?: string;
};

const useTreeInfoSearchParameters = (
  urlFrom: TreeDetailsRouteFrom,
): TreeSearchParameters => {
  const {
    origin,
    treeInfo: { gitUrl, gitBranch },
  } = useSearch({ from: urlFrom });

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
  treeName,
  gitBranch,
  treeId,
  treeSearchParameters,
  filter = {},
  variant,
  urlFrom,
}: {
  treeName: string;
  gitBranch: string;
  treeId: string;
  treeSearchParameters: TreeSearchParameters;
  filter: TTreeDetailsFilter;
  variant: TreeDetailsVariants;
  urlFrom: TreeDetailsRouteFrom;
}): Promise<TreeDetailsFullData> => {
  const backendCompatibleFilters = mapFiltersKeysToBackendCompatible(filter);

  const params = {
    git_branch: treeSearchParameters.gitBranch,
    git_url: treeSearchParameters.gitUrl,
    origin: treeSearchParameters.origin,
    ...backendCompatibleFilters,
  };

  const baseUrl =
    urlFrom === treeDetailsDirectRouteName
      ? `/api/tree/${treeName}/${gitBranch}/${treeId}`
      : `/api/tree/${treeId}`;

  const urlTable: Record<TreeDetailsVariants, string> = {
    full: `${baseUrl}/full`,
    builds: `${baseUrl}/builds`,
    boots: `${baseUrl}/boots`,
    tests: `${baseUrl}/tests`,
    summary: `${baseUrl}/summary`,
  };

  const data = await RequestData.get<TreeDetailsFullData>(urlTable[variant], {
    params,
  });

  return data;
};

type TreeDetailsResponse<T extends keyof TreeDetailsResponseTable> =
  TreeDetailsResponseTable[T];

export type UseTreeDetailsWithoutVariant = {
  treeName: string;
  gitBranch: string;
  treeId: string;
  urlFrom: TreeDetailsRouteFrom;
  filter?: TFilter;
  enabled?: boolean;
};

type UseTreeDetailsParameters<T extends TreeDetailsVariants> = {
  variant: T;
} & UseTreeDetailsWithoutVariant;

export const useTreeDetails = <T extends TreeDetailsVariants>({
  treeId,
  treeName,
  gitBranch,
  filter = {},
  enabled = true,
  variant,
  urlFrom,
}: UseTreeDetailsParameters<T>): UseQueryResult<TreeDetailsResponse<T>> => {
  const testFilter = getTargetFilter(filter, 'test');
  const treeDetailsFilter = getTargetFilter(filter, 'treeDetails');
  const treeSearchParameters = useTreeInfoSearchParameters(urlFrom);

  return useQuery({
    queryKey: [
      'treeTests',
      treeName,
      gitBranch,
      treeId,
      treeSearchParameters,
      testFilter,
      treeDetailsFilter,
      variant,
      urlFrom,
    ],
    queryFn: () =>
      fetchTreeDetails({
        treeName,
        gitBranch,
        treeId,
        treeSearchParameters,
        variant,
        urlFrom,
        filter: {
          ...testFilter,
          ...treeDetailsFilter,
        },
      }),
    enabled,
    refetchOnWindowFocus: false,
    // TODO: check the cases when the real previous data is null/undefined
    placeholderData: previousData => previousData,
  });
};

const fetchLogFiles = async (logUrl: string): Promise<BuildCountsResponse> => {
  const data = await RequestData.get<BuildCountsResponse>(
    `/api/log-downloader/`,
    {
      params: {
        log_download_url: logUrl,
      },
    },
  );

  return data;
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
    retry: retryHandler(1),
    queryFn: () => fetchLogFiles(logUrl),
  });
};
