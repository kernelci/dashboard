import { FormattedMessage } from 'react-intl';

import { useParams } from '@tanstack/react-router';

import { Skeleton } from '@/components/Skeleton';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import {
  MemoizedStatusChart,
  MemoizedErrorCountList,
  MemoizedConfigList,
  MemoizedErrorsSummary,
  MemoizedPlatformsWithError,
} from '@/pages/TreeDetails/Tabs/TestCards';

import TestsTable from '@/components/Table/TestsTable';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';
import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';

interface TestsTabProps {
  reqFilter: Record<string, string[]>;
}

const TestsTab = ({ reqFilter }: TestsTabProps): JSX.Element => {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { isLoading, data, error } = useTestsTab(treeId ?? '', reqFilter);

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
      <DesktopGrid>
        <div>
          <MemoizedStatusChart
            title={<FormattedMessage id="testsTab.testStatus" />}
            statusCounts={data.testStatusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="global.configs" />}
            configStatusCounts={data.testConfigs}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.testArchSummary}
          />
        </div>
        <div>
          <CommitNavigationGraph />
          <MemoizedPlatformsWithError
            title={<FormattedMessage id="testsTab.platformsErrors" />}
            platformsWithError={data.testPlatformsWithErrors}
          />
          <MemoizedErrorCountList
            title={<FormattedMessage id="testsTab.fail" />}
            errorMessageCounts={data.testFailReasons}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusChart
          title={<FormattedMessage id="testsTab.testStatus" />}
          statusCounts={data.testStatusSummary}
        />
        <CommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="global.configs" />}
              configStatusCounts={data.testConfigs}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.testArchSummary}
            />
          </div>
          <div>
            <MemoizedPlatformsWithError
              title={<FormattedMessage id="testsTab.platformsErrors" />}
              platformsWithError={data.testPlatformsWithErrors}
            />
            <MemoizedErrorCountList
              title={<FormattedMessage id="testsTab.fail" />}
              errorMessageCounts={data.testFailReasons}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>

      <TestsTable testHistory={data.testHistory} />
    </div>
  );
};

export default TestsTab;
