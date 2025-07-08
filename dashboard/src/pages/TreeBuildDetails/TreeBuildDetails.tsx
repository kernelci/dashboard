import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useRouterState, useSearch } from '@tanstack/react-router';

import { useCallback, type JSX } from 'react';

import BuildDetails from '@/components/BuildDetails/BuildDetails';
import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';
import { RedirectFrom } from '@/types/general';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';
import { useSearchStore } from '@/hooks/store/useSearchStore';

const TreeBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/build/$buildId' });
  const treeId = useRouterState({ select: s => s.location.state.id });
  const previousSearch = useSearchStore(s => s.previousSearch);

  const navigate = useNavigate({ from: '/tree/$treeId/build/$buildId' });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: testId,
        treeId: treeId,
      },
      search: s => s,
      state: s => s,
    }),
    [treeId],
  );

  const onClickFilter = useCallback(
    (filter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: filter,
            },
          };
        },
        state: { id: treeId, from: RedirectFrom.Tree },
      });
    },
    [navigate, treeId],
  );

  return (
    <BuildDetails
      breadcrumb={
        <MemoizedTreeBreadcrumb
          searchParams={previousSearch}
          locationMessage="buildDetails.buildDetails"
        />
      }
      onClickFilter={onClickFilter}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      getTestTableRowLink={getTestTableRowLink}
    />
  );
};

export default TreeBuildDetails;
