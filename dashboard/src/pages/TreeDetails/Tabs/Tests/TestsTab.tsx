import { FormattedMessage } from 'react-intl';

import { useParams, useSearch } from '@tanstack/react-router';

import { Skeleton } from '@/components/Skeleton';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import {
  MemoizedStatusChart,
  MemoizedErrorCountList,
  MemoizedConfigList,
  MemoizedErrorsSummary,
  MemoizedLineChartCard,
  MemoizedPlatformsWithError,
} from '@/pages/TreeDetails/Tabs/TestCards';

import TestsTable from '@/components/Table/TestsTable';

const TestsTab = (): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { origin, treeInfo } = useSearch({
    from: '/tree/$treeId/',
  });
  const { isLoading, data, error } = useTestsTab(
    treeId ?? '',
    origin,
    treeInfo.gitBranch ?? '',
    treeInfo.gitUrl ?? '',
  );

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.success" />
      </div>
    );
  }

  if (isLoading)
    return (
      <Skeleton>
        <FormattedMessage id="global.loading" />
      </Skeleton>
    );

  if (!data) return <div />;

  if (data.testHistory.length < 1) {
    return (
      <BaseCard
        title={<FormattedMessage id="global.info" />}
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
            <FormattedMessage id="testsTab.noTest" />
          </p>
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-8 pt-4">
      <div className="md:columns-2">
        <MemoizedStatusChart
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={data.statusCounts}
        />
        <MemoizedConfigList
          title={<FormattedMessage id="global.configs" />}
          configCounts={data.configCounts}
        />
        <MemoizedErrorsSummary
          title={<FormattedMessage id="testsTab.errorsSummary" />}
          errorCountPerArchitecture={data.errorCountPerArchitecture}
          compilersPerArchitecture={data.compilersPerArchitecture}
        />
        <MemoizedLineChartCard
          title={<FormattedMessage id="testsTab.testHistory" />}
          testHistory={data.testHistory}
        />
        <MemoizedPlatformsWithError
          title={<FormattedMessage id="testsTab.platformsErrors" />}
          platformsWithError={data.platformsWithError}
        />
        <MemoizedErrorCountList
          title={<FormattedMessage id="testsTab.fail" />}
          errorMessageCounts={data.errorMessageCounts}
        />
      </div>

      <TestsTable treeId={treeId} />
    </div>
  );
};

export default TestsTab;
