import { useQuery, UseQueryResult } from '@tanstack/react-query';

import type { Tree } from '../types/tree/Tree';

import http from "./api"

const fetchTreeCheckoutData = async (): Promise<Tree[]> => {
    const res = await http.get('/api/tree/');
    return res.data;
}

export const useTreeTable = (): UseQueryResult => {
  return useQuery({ queryKey: ['treeData'], queryFn: fetchTreeCheckoutData });
};
