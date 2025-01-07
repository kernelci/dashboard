import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  TTreeDetailsFilter,
  BuildCountsResponse,
  TTreeTestsFullData,
  LogFilesResponse,
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

function assertTreeSearchParameters(
  treeSearchParameters: TreeSearchParameters,
  locationMessage: string,
): asserts treeSearchParameters is Required<TreeSearchParameters> {
  if (!treeSearchParameters.gitUrl) {
    throw new Error(`Git URL is required in ${locationMessage}`);
  }
  if (!treeSearchParameters.gitBranch) {
    throw new Error(`Git Branch is required in ${locationMessage}`);
  }
}

const fetchTreeDetails = async (
  treeId: string,
  treeSearchParameters: TreeSearchParameters,
  filter: TTreeDetailsFilter = {},
): Promise<TTreeTestsFullData> => {
  assertTreeSearchParameters(
    treeSearchParameters,
    'fetchTreeDetails - useSearchTab',
  );

  const backendCompatibleFilters = mapFiltersKeysToBackendCompatible(filter);

  const params = {
    git_branch: treeSearchParameters.gitBranch,
    git_url: treeSearchParameters.gitUrl,
    origin: treeSearchParameters.origin,
    ...backendCompatibleFilters,
  };

  const res = await http.get<TTreeTestsFullData>(`/api/tree/${treeId}/full`, {
    params: params,
  });

  return res.data;
};

export const useTreeDetails = ({
  treeId,
  filter = {},
  enabled = true,
}: {
  treeId: string;
  filter?: TFilter;
  enabled?: boolean;
}): UseQueryResult<TTreeTestsFullData> => {
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
    ],
    queryFn: () =>
      fetchTreeDetails(treeId, treeSearchParameters, {
        ...testFilter,
        ...treeDetailsFilter,
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
