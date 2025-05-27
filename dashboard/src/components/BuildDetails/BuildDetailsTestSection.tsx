import { useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { JSX } from 'react';

import { Separator } from '@/components/ui/separator';

import { useBuildTests } from '@/api/buildTests';

import type {
  TableFilter,
  PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import { TestsTable } from '@/components/TestsTable/TestsTable';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

interface IBuildDetailsTestSection {
  buildId: string;
  onClickFilter: (filter: PossibleTableFilters) => void;
  tableFilter: TableFilter;
  getRowLink: (testId: string) => LinkProps;
}

const BuildDetailsTestSection = ({
  buildId,
  onClickFilter,
  tableFilter,
  getRowLink,
}: IBuildDetailsTestSection): JSX.Element => {
  const intl = useIntl();
  const { data, error, status, isLoading } = useBuildTests(buildId);

  return (
    <div>
      <span className="text-2xl font-bold">
        {intl.formatMessage({ id: 'buildDetails.testResults' })}
      </span>
      <Separator className="bg-dark-gray my-4" />
      <QuerySwitcher
        skeletonClassname="h-[100px]"
        status={status}
        data={data}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel="buildDetails.noTestResults"
          />
        }
      >
        <div className="flex flex-col gap-6">
          <TestsTable
            tableKey="buildDetailsTests"
            testHistory={data}
            onClickFilter={onClickFilter}
            filter={tableFilter.testsTable}
            getRowLink={getRowLink}
          />
        </div>
      </QuerySwitcher>
    </div>
  );
};

export default BuildDetailsTestSection;
