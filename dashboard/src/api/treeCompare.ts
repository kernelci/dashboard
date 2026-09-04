import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  TreeCompareBuildDiffApiRow,
  TreeCompareData,
  TreeCompareTestDiffApiRow,
} from '@/types/tree/TreeCompare';

import { RequestData } from './commonRequest';

type CompareParams = {
  treeName: string;
  branch: string;
  hashA: string;
  hashB: string;
  origin: string;
};

type CompareParamsRequestParams = {
  hash_a: string;
  hash_b: string;
  origin: string;
};

const compareParams = ({
  hashA,
  hashB,
  origin,
}: Pick<
  CompareParams,
  'hashA' | 'hashB' | 'origin'
>): CompareParamsRequestParams => ({
  hash_a: hashA,
  hash_b: hashB,
  origin,
});

const fetchTreeCompare = async ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): Promise<TreeCompareData> =>
  RequestData.get<TreeCompareData>(`/api/tree/${treeName}/${branch}/compare`, {
    params: compareParams({ hashA, hashB, origin }),
  });

const fetchTreeCompareBuilds = async ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): Promise<TreeCompareBuildDiffApiRow[]> =>
  RequestData.get<TreeCompareBuildDiffApiRow[]>(
    `/api/tree/${treeName}/${branch}/compare/builds`,
    { params: compareParams({ hashA, hashB, origin }) },
  );

const fetchTreeCompareBoots = async ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): Promise<TreeCompareTestDiffApiRow[]> =>
  RequestData.get<TreeCompareTestDiffApiRow[]>(
    `/api/tree/${treeName}/${branch}/compare/boots`,
    { params: compareParams({ hashA, hashB, origin }) },
  );

const fetchTreeCompareTests = async ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): Promise<TreeCompareTestDiffApiRow[]> =>
  RequestData.get<TreeCompareTestDiffApiRow[]>(
    `/api/tree/${treeName}/${branch}/compare/tests`,
    { params: compareParams({ hashA, hashB, origin }) },
  );

export const useTreeCompare = ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): UseQueryResult<TreeCompareData> =>
  useQuery({
    queryKey: ['treeCompare', treeName, branch, hashA, hashB, origin],
    queryFn: () => fetchTreeCompare({ treeName, branch, hashA, hashB, origin }),
    enabled: !!hashA && !!hashB,
  });

export const useTreeCompareBuilds = ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): UseQueryResult<TreeCompareBuildDiffApiRow[]> =>
  useQuery({
    queryKey: ['treeCompareBuilds', treeName, branch, hashA, hashB, origin],
    queryFn: () =>
      fetchTreeCompareBuilds({ treeName, branch, hashA, hashB, origin }),
    enabled: !!hashA && !!hashB,
  });

export const useTreeCompareBoots = ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): UseQueryResult<TreeCompareTestDiffApiRow[]> =>
  useQuery({
    queryKey: ['treeCompareBoots', treeName, branch, hashA, hashB, origin],
    queryFn: () =>
      fetchTreeCompareBoots({ treeName, branch, hashA, hashB, origin }),
    enabled: !!hashA && !!hashB,
  });

export const useTreeCompareTests = ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: CompareParams): UseQueryResult<TreeCompareTestDiffApiRow[]> =>
  useQuery({
    queryKey: ['treeCompareTests', treeName, branch, hashA, hashB, origin],
    queryFn: () =>
      fetchTreeCompareTests({ treeName, branch, hashA, hashB, origin }),
    enabled: !!hashA && !!hashB,
  });
