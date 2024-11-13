import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  BuildsTab,
  TTreeDetailsFilter,
  TTestByCommitHashResponse,
  TTreeCommitHistoryResponse,
  BuildCountsResponse,
  TTreeTestsFullData,
  LogFilesResponse,
} from '@/types/tree/TreeDetails';

import type { TPathTests } from '@/types/general';

import { getTargetFilter } from '@/utils/filters';

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

const fetchTreeDetailData = async (
  treeId: string,
  treeSearchParameters: TreeSearchParameters,
  filter: TTreeDetailsFilter | Record<string, never>,
): Promise<BuildsTab> => {
  const filtersFormatted = mapFiltersKeysToBackendCompatible(filter);

  const params = {
    origin: treeSearchParameters.origin,
    git_url: treeSearchParameters.gitUrl,
    git_branch: treeSearchParameters.gitBranch,
    ...filtersFormatted,
  };

  assertTreeSearchParameters(treeSearchParameters, 'useBuildsTab');

  const res = await http.get(`/api/tree/${treeId}`, { params: params });
  return res.data;
};

// TODO, remove this function, is just a step further towards the final implementation
const mapFiltersKeysToBackendCompatible = (
  filter: TTreeDetailsFilter | Record<string, never>,
): Record<string, string[]> => {
  const filterParam: { [key: string]: string[] } = {};

  Object.keys(filter).forEach(key => {
    const filterList = filter[key as keyof TTreeDetailsFilter];
    filterList?.forEach(value => {
      if (!filterParam[`filter_${key}`])
        filterParam[`filter_${key}`] = [value.toString()];
      else filterParam[`filter_${key}`].push(value.toString());
    });
  });

  return filterParam;
};

export const useBuildsTab = ({
  treeId,
  filter = {},
  enabled = true,
}: {
  treeId: string;
  filter?: TTreeDetailsFilter | Record<string, never>;
  enabled?: boolean;
}): UseQueryResult<BuildsTab> => {
  const detailsFilter = getTargetFilter(filter, 'treeDetails');

  const treeSearchParameters = useTreeSearchParameters();

  return useQuery({
    queryKey: ['treeData', treeId, detailsFilter, treeSearchParameters],
    queryFn: () =>
      fetchTreeDetailData(treeId, treeSearchParameters, detailsFilter),
    enabled,
  });
};

const fetchTreeTestsData = async (
  treeId: string,
  treeSearchParameters: TreeSearchParameters,
  filter: TTreeDetailsFilter = {},
): Promise<TTreeTestsFullData> => {
  assertTreeSearchParameters(
    treeSearchParameters,
    'fetchTreeTestsData - useSearchTab',
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

export const useTestsTab = ({
  treeId,
  filter,
  enabled = true,
}: {
  treeId: string;
  filter: TTreeDetailsFilter;
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
      fetchTreeTestsData(treeId, treeSearchParameters, {
        ...testFilter,
        ...treeDetailsFilter,
      }),
    enabled,
  });
};

const fetchTestsByTreeAndCommitHash = async (
  commitHash: string,
  params?: {
    path?: string;
    origin?: string;
    git_url?: string;
    git_branch?: string;
  },
): Promise<TTestByCommitHashResponse> => {
  const res = await http.get<TTestByCommitHashResponse>(
    `/api/tests/${commitHash}`,
    { params },
  );

  return res.data;
};

export const useTestsByTreeAndCommitHash = (
  commitHash: string,
  isBoot: boolean,
  origin?: string,
  git_url?: string,
  git_branch?: string,
): UseQueryResult<TTestByCommitHashResponse> => {
  const params = {
    origin: origin,
    git_url: git_url,
    git_branch: git_branch,
    path: isBoot ? 'boot' : '',
  };
  return useQuery({
    queryKey: ['testsByTreeAndCommitHash', commitHash, params],
    queryFn: () => fetchTestsByTreeAndCommitHash(commitHash, params),
  });
};

type TTreeData = {
  git_commit_hash?: string;
  patchset?: string;
  path?: string;
  git_repository_url: string;
  git_repository_branch: string;
  origin: string;
};

const fetchTreeTestData = async (params?: TTreeData): Promise<TPathTests[]> => {
  const res = await http.get<TPathTests[]>(`/api/tree/tests/`, {
    params,
  });

  return res.data;
};

export const useTreeTest = (
  git_commit_hash: TTreeData['git_commit_hash'],
  path: TTreeData['path'],
  git_repository_branch: TTreeData['git_repository_branch'],
  git_repository_url: TTreeData['git_repository_url'],
  origin: TTreeData['origin'],
): UseQueryResult<TPathTests[]> => {
  return useQuery({
    queryKey: [
      'treeGroupedTests',
      git_commit_hash,
      path,
      git_repository_url,
      git_repository_branch,
      origin,
    ],
    queryFn: () =>
      fetchTreeTestData({
        git_commit_hash,
        path,
        git_repository_url,
        git_repository_branch,
        origin,
      }),
  });
};

const fetchTreeCommitHistory = async (
  commitHash: string,
  origin: string,
  gitUrl: string,
  gitBranch: string,
  filters: TTreeDetailsFilter,
): Promise<TTreeCommitHistoryResponse> => {
  const filtersFormatted = mapFiltersKeysToBackendCompatible(filters);

  const params = {
    origin,
    git_url: gitUrl,
    git_branch: gitBranch,
    ...filtersFormatted,
  };

  const res = await http.get<TTreeCommitHistoryResponse>(
    `/api/tree/${commitHash}/commits`,
    {
      params,
    },
  );
  return res.data;
};

export const useTreeCommitHistory = (
  {
    commitHash,
    origin,
    gitUrl,
    gitBranch,
    filter,
  }: {
    commitHash: string;
    origin: string;
    gitUrl: string;
    gitBranch: string;
    filter: TTreeDetailsFilter;
  },
  { enabled = true },
): UseQueryResult<TTreeCommitHistoryResponse> => {
  const testFilter = getTargetFilter(filter, 'test');
  const treeDetailsFilter = getTargetFilter(filter, 'treeDetails');

  const filters = {
    ...treeDetailsFilter,
    ...testFilter,
  };

  return useQuery({
    queryKey: [
      'treeCommitHistory',
      commitHash,
      origin,
      gitUrl,
      gitBranch,
      filters,
    ],
    enabled,
    queryFn: () =>
      fetchTreeCommitHistory(commitHash, origin, gitUrl, gitBranch, filters),
  });
};

const fetchBuildStatusCount = async (
  buildId: string,
): Promise<BuildCountsResponse> => {
  const res = await http.get<BuildCountsResponse>(
    `/api/build/${buildId}/status-count`,
  );
  return res.data;
};

export const useBuildStatusCount = (
  {
    buildId,
  }: {
    buildId: string;
  },
  { enabled = true },
): UseQueryResult<BuildCountsResponse> => {
  return useQuery({
    queryKey: [buildId],
    enabled,
    queryFn: () => fetchBuildStatusCount(buildId),
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
