import { FormattedMessage, useIntl } from 'react-intl';

import { RiProhibited2Line } from 'react-icons/ri';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { Separator } from '@/components/ui/separator';

import { useBuildTests } from '@/api/buildTests';

import { TestsTableFilter } from '@/types/tree/TreeDetails';

import { TestsTable } from '../TreeDetails/Tabs/Tests/TestsTable';

interface IBuildDetailsTestSection {
  buildId: string;
}

const NoTestFound = (): JSX.Element => (
  <div className="flex flex-col items-center py-6 text-weakGray">
    <RiProhibited2Line className="h-14 w-14" />
    <h1 className="text-2xl font-semibold">
      <FormattedMessage id={'buildDetails.noTestResults'} />
    </h1>
  </div>
);

const BuildDetailsTestSection = ({
  buildId,
}: IBuildDetailsTestSection): JSX.Element => {
  const intl = useIntl();
  const { data, error } = useBuildTests(buildId);
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/build/$buildId/',
  });

  const navigate = useNavigate({ from: '/tree/$treeId/build/$buildId' });

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              bootsTable: previousParams.tableFilter.bootsTable,
              buildsTable: previousParams.tableFilter.buildsTable,
              testsTable: filter,
            },
          };
        },
      });
    },
    [navigate],
  );

  const hasTest = data && data.length > 0 && !error;
  return (
    <>
      <span className="text-2xl font-bold">
        {intl.formatMessage({ id: 'buildDetails.testResults' })}
      </span>
      <Separator className="my-6 bg-darkGray" />
      {hasTest ? (
        <div className="flex flex-col gap-6">
          <TestsTable
            testHistory={data}
            onClickFilter={onClickFilter}
            tableFilter={tableFilter}
          />
        </div>
      ) : (
        <NoTestFound />
      )}
    </>
  );
};

export default BuildDetailsTestSection;
