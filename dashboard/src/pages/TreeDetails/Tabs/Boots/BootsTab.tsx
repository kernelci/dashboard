import { FormattedMessage } from 'react-intl';

import { useParams, useSearch } from '@tanstack/react-router';

import { useBootsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import { Skeleton } from '@/components/Skeleton';

import {
  MemoizedConfigList,
  MemoizedErrorCountList,
  MemoizedErrorsSummary,
  MemoizedLineChartCard,
  MemoizedPlatformsWithError,
  MemoizedStatusChart,
} from '@/pages/TreeDetails/Tabs/TestCards';
import BootsTable from '@/components/Table/BootsTable';

interface BootsTabProps {
  reqFilter: Record<string, string[]>;
}

const BootsTab = ({ reqFilter }: BootsTabProps): JSX.Element => {
  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });
  const { origin, treeInfo } = useSearch({
    from: '/tree/$treeId/',
  });
  const { isLoading, data, error } = useBootsTab(
    treeId ?? '',
    origin,
    treeInfo.gitBranch ?? '',
    treeInfo.gitUrl ?? '',
    reqFilter,
  );

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
      <div className="md:columns-2">
        <MemoizedStatusChart
          title={<FormattedMessage id="bootsTab.bootStatus" />}
          statusCounts={data.statusCounts}
        />
        <MemoizedConfigList
          title={<FormattedMessage id="bootsTab.configs" />}
          configCounts={data.configCounts}
        />
        <MemoizedErrorsSummary
          title={<FormattedMessage id="bootsTab.errorsSummary" />}
          errorCountPerArchitecture={data.errorCountPerArchitecture}
          compilersPerArchitecture={data.compilersPerArchitecture}
        />
        <MemoizedLineChartCard
          title={<FormattedMessage id="bootsTab.bootHistory" />}
          testHistory={data.testHistory}
        />
        <MemoizedPlatformsWithError
          title={<FormattedMessage id="bootsTab.platformsFailingAtBoot" />}
          platformsWithError={data.platformsWithError}
        />
        <MemoizedErrorCountList
          title={<FormattedMessage id="bootsTab.fail" />}
          errorMessageCounts={data.errorMessageCounts}
        />
      </div>
      <BootsTable treeId={treeId} isBootTable={true} />
    </div>
  );
};

export default BootsTab;
