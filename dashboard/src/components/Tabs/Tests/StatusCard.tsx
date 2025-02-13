import { memo, useMemo, type JSX } from 'react';

import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';

import type { StatusChartValues } from '@/components/StatusChart/StatusCharts';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';
import { groupStatus } from '@/utils/status';
import type { TTreeTestsData } from '@/types/tree/TreeDetails';

interface IStatusChart extends Pick<TTreeTestsData, 'statusCounts'> {
  title: IBaseCard['title'];
}
const StatusCard = ({ statusCounts, title }: IStatusChart): JSX.Element => {
  const groupedStatusCounts = useMemo(
    () =>
      groupStatus({
        doneCount: statusCounts.DONE,
        errorCount: statusCounts.ERROR,
        failCount: statusCounts.FAIL,
        missCount: statusCounts.MISS,
        passCount: statusCounts.PASS,
        skipCount: statusCounts.SKIP,
        nullCount: statusCounts.NULL,
      }),
    [
      statusCounts.DONE,
      statusCounts.ERROR,
      statusCounts.FAIL,
      statusCounts.MISS,
      statusCounts.NULL,
      statusCounts.PASS,
      statusCounts.SKIP,
    ],
  );

  const chartElements = useMemo(
    () =>
      [
        {
          label: 'bootsTab.success',
          value: groupedStatusCounts.successCount,
          color: Colors.Green,
        },
        {
          label: 'global.failed',
          value: groupedStatusCounts.failedCount,
          color: Colors.Red,
        },
        {
          label: 'global.inconclusive',
          value: groupedStatusCounts.inconclusiveCount ?? 0,
          color: Colors.Gray,
        },
      ] satisfies StatusChartValues[],
    [
      groupedStatusCounts.failedCount,
      groupedStatusCounts.inconclusiveCount,
      groupedStatusCounts.successCount,
    ],
  );

  const filteredChartElements = useMemo(
    () =>
      chartElements.filter(chartElement => {
        return chartElement.value > 0;
      }),
    [chartElements],
  );

  const totalCount = useMemo(
    () =>
      Object.values(statusCounts).reduce(
        (accumulator: number, count) => accumulator + (count ?? 0),
        0,
      ),
    [statusCounts],
  );

  return (
    <BaseCard
      title={title}
      content={
        <StatusChartMemoized
          type="chart"
          elements={filteredChartElements}
          pieCentralLabel="Statuses"
          pieCentralDescription={<>{totalCount}</>}
        />
      }
    />
  );
};

const MemoizedStatusChart = memo(StatusCard);

export default MemoizedStatusChart;
