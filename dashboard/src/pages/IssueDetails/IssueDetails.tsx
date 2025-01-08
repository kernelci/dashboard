import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { IssueDetails } from '@/components/IssueDetails/IssueDetails';
import type {
  BuildsTableFilter,
  TestsTableFilter,
} from '@/types/tree/TreeDetails';
import { zTableFilterInfoDefault } from '@/types/tree/TreeDetails';

const ISSUE_ROUTE = '/issue/$issueId/version/$versionNumber';

const getBuildTableRowLink = (buildId: string): LinkProps => ({
  to: '/build/$buildId',
  params: {
    buildId: buildId,
  },
  search: s => s,
});

const getTestTableRowLink = (testId: string): LinkProps => ({
      to: '/test/$testId',
      params: {
        testId: testId,
      },
      search: s => s,
});

const IssueDetailsPage = (): JSX.Element => {
  const searchParams = useSearch({ from: ISSUE_ROUTE });
  const { issueId, versionNumber } = useParams({ from: ISSUE_ROUTE });
  const navigate = useNavigate({ from: ISSUE_ROUTE });

  const onClickTestFilter = useCallback(
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
      });
    },
    [navigate],
  );

  const onClickBuildFilter = useCallback(
    (filter: BuildsTableFilter): void => {
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
      });
    },
    [navigate],
  );

  return (
    <IssueDetails
      issueId={issueId}
      versionNumber={versionNumber}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      onClickTestFilter={onClickTestFilter}
      getTestTableRowLink={getTestTableRowLink}
      onClickBuildFilter={onClickBuildFilter}
      getBuildTableRowLink={getBuildTableRowLink}
    />
  );
};

export default IssueDetailsPage;
