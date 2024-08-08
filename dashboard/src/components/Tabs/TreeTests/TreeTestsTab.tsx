import { FormattedMessage } from 'react-intl';

import { useParams } from 'react-router-dom';

import { useTestsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';

import {
  StatusChartMemo,
  MemoizedErrorCountList,
  MemoizedConfigList,
  MemoizedErrorsSummary,
  MemoizedLineChartCard,
  MemoizedPlatformsWithError
} from '../Boots/BootsTab';

const TreeTestsTab = (): JSX.Element => {
  const { treeId } = useParams();
  const { isLoading, data, error } = useTestsTab(treeId ?? '');

  if (error || !treeId) {
    return (
      <div>
        <FormattedMessage id="bootsTab.success" />
      </div>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!data) return <div />;

  if (data.bootHistory.length < 1) {
    return (
      <BaseCard
        title=<FormattedMessage id="bootsTab.info" />
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
        <StatusChartMemo title={<>FOO</>} statusCounts={data.statusCounts} />
        <MemoizedConfigList title={<>FOO</>} configCounts={data.configCounts} />
        <MemoizedErrorsSummary
          title={<>FOO</>}
          errorCountPerArchitecture={data.errorCountPerArchitecture}
          compilersPerArchitecture={data.compilersPerArchitecture}
        />
        <MemoizedLineChartCard title={<>FOO</>} bootHistory={data.bootHistory} />
        <MemoizedPlatformsWithError
          title={<>FOO</>}
          platformsWithError={data.platformsWithError}
        />
        <MemoizedErrorCountList title={<>FOO</>} errorMessageCounts={data.errorMessageCounts} />
      </div>
    </div>
  );
};

export default TreeTestsTab;
