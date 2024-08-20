import { FormattedMessage } from 'react-intl';

import { useParams } from '@tanstack/react-router';

import { useBootsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import {
  MemoizedConfigList,
  MemoizedErrorCountList,
  MemoizedErrorsSummary,
  MemoizedLineChartCard,
  MemoizedPlatformsWithError,
  MemoizedStatusChart,
} from '@/pages/TreeDetails/Tabs/TestCards';

const BootsTab = (): JSX.Element => {
  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });
  const { isLoading, data, error } = useBootsTab(treeId ?? '');

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.success" />
      </div>
    );
  }

  if (isLoading) {
    return <FormattedMessage id="global.loading" />;
  }

  if (!data) return <div />;

  if (data.testHistory.length < 1) {
    return (
      <BaseCard
        title={<FormattedMessage id="bootsTab.info" />}
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
            ℹ️ <FormattedMessage id="bootsTab.info.description" />
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
    </div>
  );
};

export default BootsTab;
