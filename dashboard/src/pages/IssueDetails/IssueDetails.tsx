import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { IssueDetails } from '@/components/IssueDetails/IssueDetails';
import {
  zTableFilterInfoDefault,
  type TestsTableFilter,
} from '@/types/tree/TreeDetails';

const CURRENT_ROUTE = '/issue/$issueId/version/$versionNumber';

const IssueDetailsPage = (): JSX.Element => {
  const searchParams = useSearch({ from: CURRENT_ROUTE });
  const { issueId, versionNumber } = useParams({ from: CURRENT_ROUTE });
  const navigate = useNavigate({ from: CURRENT_ROUTE });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/test/$testId',
      params: {
        testId: testId,
      },
      search: s => s,
    }),
    [],
  );

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

  return (
    <IssueDetails
      issueId={issueId}
      versionNumber={versionNumber}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      onClickTestFilter={onClickTestFilter}
      getTestTableRowLink={getTestTableRowLink}
    />
  );
};

export default IssueDetailsPage;
