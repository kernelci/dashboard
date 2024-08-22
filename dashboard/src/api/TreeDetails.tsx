import { useQuery, UseQueryResult } from '@tanstack/react-query';

import {
  TTreeTestsData,
  TreeDetails,
  TTreeDetailsFilter,
  TTestByCommitHashResponse,
} from '@/types/tree/TreeDetails';

import { TPathTests } from '@/types/general';

import http from './api';

const fetchTreeDetailData = async (
  treeId: string,
  filter: TTreeDetailsFilter | Record<string, never>,
): Promise<TreeDetails> => {
  const filterParam = new URLSearchParams();

  Object.keys(filter).forEach(key => {
    const filterList = filter[key as keyof TTreeDetailsFilter];
    filterList?.forEach(value =>
      filterParam.append(`filter_${key}`, value.toString()),
    );
  });

  const res = await http.get(`/api/tree/${treeId}`, { params: filterParam });
  return res.data;
};

export const useTreeDetails = (
  treeId: string,
  filter: TTreeDetailsFilter | Record<string, never> = {},
): UseQueryResult<TreeDetails> => {
  return useQuery({
    queryKey: ['treeData', treeId, filter],
    queryFn: () => fetchTreeDetailData(treeId, filter),
  });
};

const fetchTreeTestsData = async (
  treeId: string,
  params?: { path?: string },
): Promise<TTreeTestsData> => {
  const res = await http.get<TTreeTestsData>(`/api/tree/${treeId}/tests`, {
    params,
  });

  return res.data;
};

export const useBootsTab = (treeId: string): UseQueryResult<TTreeTestsData> => {
  const params = { path: 'boot.' };

  return useQuery({
    queryKey: ['treeBootTests', treeId, params],
    queryFn: () => fetchTreeTestsData(treeId, params),
  });
};

export const useTestsTab = (treeId: string): UseQueryResult<TTreeTestsData> => {
  return useQuery({
    queryKey: ['treeTests', treeId],
    queryFn: () => fetchTreeTestsData(treeId),
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
};

const fetchTreeTestData = async (params?: TTreeData): Promise<TPathTests[]> => {
  const res = await http.get<TPathTests[]>(`/api/tree/tests/`, {
    params,
  });

  return res.data;
};

export const useTreeTest = (
  git_commit_hash: TTreeData['git_commit_hash'],
  patchset: TTreeData['patchset'],
  path: TTreeData['path'],
): UseQueryResult<TPathTests[]> => {
  return useQuery({
    queryKey: ['treeRevisionTests', git_commit_hash, patchset, path],
    queryFn: () => fetchTreeTestData({ git_commit_hash, patchset, path }),
  });
};
