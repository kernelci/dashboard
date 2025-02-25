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

const TreeBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/build/$buildId' });
  const historyState = useRouterState({ select: s => s.location.state });
  const treeId = historyState.id;

  const navigate = useNavigate({ from: '/tree/$treeId/build/$buildId' });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: testId,
        treeId: treeId,
      },
      search: s => s,
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
          searchParams={searchParams}
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
