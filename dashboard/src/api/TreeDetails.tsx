import { useQuery, UseQueryResult } from '@tanstack/react-query';

import {
  TTreeTestsData,
  BuildsTab,
  TTreeDetailsFilter,
  TTestByCommitHashResponse,
  TTreeCommitHistoryResponse,
  BuildCountsResponse,
} from '@/types/tree/TreeDetails';

import { TPathTests } from '@/types/general';

import { getTargetFilter } from '@/utils/filters';

import http from './api';

const fetchTreeDetailData = async (
  treeId: string,
  filter: TTreeDetailsFilter | Record<string, never>,
): Promise<BuildsTab> => {
  const filterParam = mapFiltersToUrlSearchParams(filter);

  const res = await http.get(`/api/tree/${treeId}`, { params: filterParam });
  return res.data;
};

const mapFiltersToUrlSearchParams = (
  filter: TTreeDetailsFilter | Record<string, never>,
): URLSearchParams => {
  const filterParam = new URLSearchParams();

  Object.keys(filter).forEach(key => {
    const filterList = filter[key as keyof TTreeDetailsFilter];
    filterList?.forEach(value =>
      filterParam.append(`filter_${key}`, value.toString()),
    );
  });

  return filterParam;
};

export const useBuildsTab = (
  treeId: string,
  filter: TTreeDetailsFilter | Record<string, never> = {},
): UseQueryResult<BuildsTab> => {
  const detailsFilter = getTargetFilter(filter, 'treeDetails');

  return useQuery({
    queryKey: ['treeData', treeId, detailsFilter],
    queryFn: () => fetchTreeDetailData(treeId, detailsFilter),
  });
};

const fetchTreeTestsData = async (
  treeId: string,
  params?: {
    origin: string;
    git_branch: string;
    git_url: string;
  },
  filter: TTreeDetailsFilter = {},
): Promise<TTreeTestsData> => {
  const urlParams = mapFiltersToUrlSearchParams(filter);
  if (params !== undefined) {
    Object.entries(params).forEach(([k, v]) =>
      urlParams.append(k, v.toString()),
    );
  }
  const res = await http.get<TTreeTestsData>(`/api/tree/${treeId}/tests`, {
    params: urlParams,
  });

  return res.data;
};

export const useBootsTab = (
  treeId: string,
  origin: string,
  git_branch: string,
  git_url: string,
  filter: TTreeDetailsFilter,
): UseQueryResult<TTreeTestsData> => {
  const params = {
    path: 'boot.',
    origin: origin,
    git_branch: git_branch,
    git_url: git_url,
  };

  const bootsFilter = getTargetFilter(filter, 'boot');

  return useQuery({
    queryKey: ['treeBootTests', treeId, bootsFilter, params],
    queryFn: () => fetchTreeTestsData(treeId, params, bootsFilter),
  });
};

export const useTestsTab = (
  treeId: string,
  origin: string,
  git_branch: string,
  git_url: string,
  filter: TTreeDetailsFilter,
): UseQueryResult<TTreeTestsData> => {
  const params = {
    origin: origin,
    git_branch: git_branch,
    git_url: git_url,
  };
  const testFilter = getTargetFilter(filter, 'test');

  return useQuery({
    queryKey: ['treeTests', treeId, params, testFilter],
    queryFn: () => fetchTreeTestsData(treeId, params, testFilter),
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
): Promise<TTreeCommitHistoryResponse> => {
  const res = await http.get<TTreeCommitHistoryResponse>(
    `/api/tree/${commitHash}/commits`,
    {
      params: {
        origin,
        git_url: gitUrl,
        git_branch: gitBranch,
      },
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
  }: {
    commitHash: string;
    origin: string;
    gitUrl: string;
    gitBranch: string;
  },
  { enabled = true },
): UseQueryResult<TTreeCommitHistoryResponse> => {
  return useQuery({
    queryKey: ['treeCommitHistory', commitHash, origin, gitUrl, gitBranch],
    enabled,
    queryFn: () =>
      fetchTreeCommitHistory(commitHash, origin, gitUrl, gitBranch),
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
