import { FormattedMessage } from 'react-intl';

import { useParams } from '@tanstack/react-router';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import { Skeleton } from '@/components/Skeleton';

import {
  MemoizedConfigList,
  MemoizedErrorsSummary,
  MemoizedHardwareTested,
  MemoizedIssuesList,
  MemoizedStatusChart,
} from '@/pages/TreeDetails/Tabs/TestCards';
// import BootsTable from '@/components/Table/BootsTable';

import {
  DesktopGrid,
  InnerMobileGrid,
  MobileGrid,
} from '@/pages/TreeDetails/Tabs/TabGrid';

import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';
import { NewBootsTable } from '@/components/NewTables/NewBootsTable';

interface BootsTabProps {
  reqFilter: Record<string, string[]>;
}

const BootsTab = ({ reqFilter }: BootsTabProps): JSX.Element => {
  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });
  const { isLoading, data, error } = useTestsTab(treeId ?? '', reqFilter);

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.error" />
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
        title={<FormattedMessage id="bootsTab.info" />}
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
            <FormattedMessage id="bootsTab.info.description" />
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
            title={<FormattedMessage id="bootsTab.bootStatus" />}
            statusCounts={data.bootStatusSummary}
          />
          <MemoizedConfigList
            title={<FormattedMessage id="bootsTab.configs" />}
            configStatusCounts={data.bootConfigs}
          />
          <MemoizedErrorsSummary
            title={<FormattedMessage id="global.summary" />}
            archCompilerErrors={data.bootArchSummary}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={data.bootIssues}
          />
        </div>
        <div>
          <CommitNavigationGraph />
          <MemoizedHardwareTested
            title={<FormattedMessage id="bootsTab.hardwareTested" />}
            environmentCompatible={data.bootEnvironmentCompatible}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <MemoizedStatusChart
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={data.bootStatusSummary}
        />
        <CommitNavigationGraph />
        <InnerMobileGrid>
          <div>
            <MemoizedConfigList
              title={<FormattedMessage id="bootsTab.configs" />}
              configStatusCounts={data.bootConfigs}
            />
            <MemoizedErrorsSummary
              title={<FormattedMessage id="global.summary" />}
              archCompilerErrors={data.bootArchSummary}
            />
            <MemoizedIssuesList
              title={<FormattedMessage id="global.issues" />}
              issues={data.bootIssues}
            />
          </div>
          <div>
            <MemoizedHardwareTested
              title={<FormattedMessage id="bootsTab.hardwareTested" />}
              environmentCompatible={data.bootEnvironmentCompatible}
            />
          </div>
        </InnerMobileGrid>
      </MobileGrid>
      <div>
        {/* <BootsTable treeId={treeId} testHistory={data.bootHistory} /> */}
        <NewBootsTable treeId={treeId} testHistory={data.bootHistory} />
      </div>
    </div>
  );
};

export default BootsTab;
