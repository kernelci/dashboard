import { memo, useCallback, useMemo, type JSX } from 'react';

import { useIntl } from 'react-intl';

import BaseCard, { type IBaseCard } from '@/components/Cards/BaseCard';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';

import type { TFilterObjectsKeys } from '@/types/general';
import type { Summary } from '@/types/commonDetails';

import { groupStatus } from '@/utils/status';

interface IStatusCard {
  title: IBaseCard['title'];
  statusCounts?: Summary['builds']['status'] | Summary['tests']['status'];
  filterStatusKey: TFilterObjectsKeys;
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}

const StatusCard = ({
  title,
  statusCounts,
  filterStatusKey,
  toggleFilterBySection,
}: IStatusCard): JSX.Element => {
  const { formatMessage } = useIntl();

  const groupedStatusCounts = useMemo(
    () =>
      groupStatus({
        doneCount: statusCounts?.DONE,
        errorCount: statusCounts?.ERROR,
        failCount: statusCounts?.FAIL,
        missCount: statusCounts?.MISS,
        passCount: statusCounts?.PASS,
        skipCount: statusCounts?.SKIP,
        nullCount: statusCounts?.NULL,
      }),
    [
      statusCounts?.DONE,
      statusCounts?.ERROR,
      statusCounts?.FAIL,
      statusCounts?.MISS,
      statusCounts?.NULL,
      statusCounts?.PASS,
      statusCounts?.SKIP,
    ],
  );

  const totalCount = useMemo(() => {
    if (!statusCounts) {
      return 0;
    }

    return Object.values(statusCounts).reduce(
      (accumulator: number, count) => accumulator + (count ?? 0),
      0,
    );
  }, [statusCounts]);

  const handleLegendClick = useCallback(
    (value: string) => {
      switch (value) {
        case formatMessage({ id: 'global.success' }):
          toggleFilterBySection('PASS', filterStatusKey);
          break;
        case formatMessage({ id: 'global.failed' }):
          toggleFilterBySection('FAIL', filterStatusKey);
          break;
        default:
          ['DONE', 'ERROR', 'MISS', 'NULL', 'SKIP'].forEach(
            inconclusiveStatus =>
              toggleFilterBySection(inconclusiveStatus, filterStatusKey),
          );
      }
    },
    [formatMessage, toggleFilterBySection, filterStatusKey],
  );

  return (
    <BaseCard
      title={title}
      content={
        <StatusChartMemoized
          type="chart"
          pieCentralLabel={formatMessage({ id: 'global.executed' })}
          pieCentralDescription={<>{totalCount}</>}
          onLegendClick={handleLegendClick}
          elements={[
            {
              value: groupedStatusCounts.successCount,
              label: 'global.success',
              color: Colors.Green,
            },
            {
              value: groupedStatusCounts.failedCount,
              label: 'global.failed',
              color: Colors.Red,
            },
            {
              value: groupedStatusCounts.inconclusiveCount,
              label: 'global.inconclusive',
              color: Colors.Gray,
            },
          ]}
        />
      }
    />
  );
};

export const MemoizedStatusCard = memo(StatusCard);
