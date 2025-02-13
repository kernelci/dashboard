import type { LinkProps } from '@tanstack/react-router';
import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import { IssueDetails } from '@/components/IssueDetails/IssueDetails';
import type { PossibleTableFilters } from '@/types/tree/TreeDetails';
import { zTableFilterInfoDefault } from '@/types/tree/TreeDetails';
import { RedirectFrom } from '@/types/general';
import { MemoizedTreeBreadcrumb } from '@/components/Breadcrumb/TreeBreadcrumb';
import { MemoizedHardwareBreadcrumb } from '@/components/Breadcrumb/HardwareBreadcrumb';

const ISSUE_ROUTE = '/issue/$issueId';

const getBuildTableRowLink = (buildId: string): LinkProps => ({
  to: '/build/$buildId',
  params: {
    buildId: buildId,
  },
  search: s => s,
  state: s => s,
});

const getTestTableRowLink = (testId: string): LinkProps => ({
  to: '/test/$testId',
  params: {
    testId: testId,
  },
  search: s => s,
  state: s => s,
});

const IssueDetailsPage = (): JSX.Element => {
  const searchParams = useSearch({ from: ISSUE_ROUTE });
  const { issueId } = useParams({ from: ISSUE_ROUTE });
  const navigate = useNavigate({ from: ISSUE_ROUTE });
  const historyState = useRouterState({ select: s => s.location.state });

  const breadcrumbComponent = useMemo(() => {
    if (historyState.id !== undefined) {
      if (historyState.from === RedirectFrom.Tree) {
        return (
          <MemoizedTreeBreadcrumb
            searchParams={searchParams}
            locationMessage="issueDetails.issueDetails"
          />
        );
      }

      if (historyState.from === RedirectFrom.Hardware) {
        return (
          <MemoizedHardwareBreadcrumb
            searchParams={searchParams}
            locationMessage="issueDetails.issueDetails"
          />
        );
      }
    }
  }, [historyState.from, historyState.id, searchParams]);

  const onClickTestFilter = useCallback(
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
        state: s => s,
      });
    },
    [navigate],
  );

  const onClickBuildFilter = useCallback(
    (filter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              buildsTable: filter,
            },
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  return (
    <IssueDetails
      issueId={issueId}
      versionNumber={searchParams.issueVersion}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      onClickTestFilter={onClickTestFilter}
      getTestTableRowLink={getTestTableRowLink}
      onClickBuildFilter={onClickBuildFilter}
      getBuildTableRowLink={getBuildTableRowLink}
      breadcrumb={breadcrumbComponent}
    />
  );
};

export default IssueDetailsPage;
