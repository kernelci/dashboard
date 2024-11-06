import { memo } from 'react';

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
const StatusChart = ({ statusCounts, title }: IStatusChart): JSX.Element => {
  const groupedStatusCounts = groupStatus({
    doneCount: statusCounts.DONE ?? 0,
    errorCount: statusCounts.ERROR ?? 0,
    failCount: statusCounts.FAIL ?? 0,
    missCount: statusCounts.MISS ?? 0,
    passCount: statusCounts.PASS ?? 0,
    skipCount: statusCounts.SKIP ?? 0,
    nullCount: statusCounts.NULL ?? 0,
  });

  const chartElements = [
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
  ] satisfies StatusChartValues[];

  const filteredChartElements = chartElements.filter(chartElement => {
    return chartElement.value > 0;
  });

  const totalCount = Object.values(statusCounts).reduce(
    (accumulator: number, count) => accumulator + (count ?? 0),
    0,
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

export default memo(StatusChart);
