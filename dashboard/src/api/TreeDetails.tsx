import { useQuery, UseQueryResult } from '@tanstack/react-query';

import {
  TTreeTestsData,
  TreeDetails,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';

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
