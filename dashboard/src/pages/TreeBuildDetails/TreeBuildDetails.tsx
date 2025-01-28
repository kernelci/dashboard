import type { LinkProps } from '@tanstack/react-router';
import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { useCallback } from 'react';

import BuildDetails from '@/components/BuildDetails/BuildDetails';
import {
  zTableFilterInfoDefault,
  type TestsTableFilter,
} from '@/types/tree/TreeDetails';
import { RedirectFrom } from '@/types/general';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';

const TreeBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/build/$buildId' });
  const { buildId } = useParams({ from: '/build/$buildId' });
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
    (filter: TestsTableFilter): void => {
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
      buildId={buildId}
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
