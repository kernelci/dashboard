import { useQueryClient } from '@tanstack/react-query';
import type { UseNavigateResult } from '@tanstack/react-router';
import { useEffect } from 'react';
import { isEqual } from 'lodash-es';

type ReferenceTable =
  | Record<string, Record<string, number> | undefined>
  | undefined;

type QueryInconsistencyInvalidatorArgs<T extends ReferenceTable> = {
  referenceData?: T;
  comparedData?: T;
  enabled?: boolean;
  navigate: UseNavigateResult<
    '/tree/$treeId' | '/hardware/$hardwareId' | '/tree/$treeName/$branch/$hash'
  >;
  navigateParams:
    | { hardwareId: string }
    | { treeId: string }
    | { treeName: string; branch: string; hash: string };
};

export const useQueryInconsistencyInvalidator = <T extends ReferenceTable>({
  referenceData: referenceData,
  comparedData: comparedData,
  navigate,
  navigateParams,
  enabled = true,
}: QueryInconsistencyInvalidatorArgs<T>): void => {
  const queryClient = useQueryClient();
  useEffect(() => {
    if (!enabled || !referenceData || !comparedData) {
      return;
    }

    const shouldInvalidate = !isEqual(referenceData, comparedData);

    if (shouldInvalidate) {
      queryClient.invalidateQueries().then(() => {
        navigate({
          search: s => s,
          state: s => {
            return {
              ...s,
              treeStatusCount: undefined,
              hardwareStatusCount: undefined,
            };
          },
          params: navigateParams,
        });
      });
    }
  }, [
    referenceData,
    comparedData,
    queryClient,
    navigate,
    enabled,
    navigateParams,
  ]);
};
