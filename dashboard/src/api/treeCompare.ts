import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type { TreeCompareData } from '@/types/tree/TreeCompare';

import { RequestData } from './commonRequest';

const fetchTreeCompare = async ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: {
  treeName: string;
  branch: string;
  hashA: string;
  hashB: string;
  origin: string;
}): Promise<TreeCompareData> =>
  RequestData.get<TreeCompareData>(`/api/tree/${treeName}/${branch}/compare`, {
    params: {
      hash_a: hashA,
      hash_b: hashB,
      origin,
    },
  });

export const useTreeCompare = ({
  treeName,
  branch,
  hashA,
  hashB,
  origin,
}: {
  treeName: string;
  branch: string;
  hashA: string;
  hashB: string;
  origin: string;
}): UseQueryResult<TreeCompareData> =>
  useQuery({
    queryKey: ['treeCompare', treeName, branch, hashA, hashB, origin],
    queryFn: () => fetchTreeCompare({ treeName, branch, hashA, hashB, origin }),
    enabled: !!hashA && !!hashB,
  });
