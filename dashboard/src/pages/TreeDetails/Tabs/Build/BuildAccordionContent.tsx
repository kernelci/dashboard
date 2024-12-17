import { memo, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import type { BuildCountsResponse } from '@/types/tree/TreeDetails';

import { useBuildStatusCount } from '@/api/treeDetails';

import type { IStatusChart } from '@/components/StatusChart/StatusCharts';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

const AccordBuildStatusChart = ({
  buildCountsData,
}: {
  buildCountsData: BuildCountsResponse;
}): JSX.Element => {
  const { build_counts } = buildCountsData;

  const chartElements: IStatusChart['elements'] = useMemo(() => {
    return [
      {
        value: build_counts.pass_tests ?? 0,
        label: 'buildAccordion.testSuccess',
        color: Colors.Green,
      },
      {
        value: build_counts.error_tests ?? 0,
        label: 'buildAccordion.testError',
        color: Colors.Red,
      },
      {
        value: build_counts.skip_tests ?? 0,
        label: 'buildAccordion.testSkipped',
        color: Colors.DimGray,
      },
      {
        value: build_counts.miss_tests ?? 0,
        label: 'buildAccordion.testMiss',
        color: Colors.Gray,
      },
      {
        value: build_counts.fail_tests ?? 0,
        label: 'buildAccordion.testFail',
        color: Colors.Yellow,
      },
      {
        value: build_counts.done_tests ?? 0,
        label: 'buildAccordion.testDone',
        color: Colors.Blue,
      },
    ];
  }, [
    build_counts.done_tests,
    build_counts.error_tests,
    build_counts.fail_tests,
    build_counts.miss_tests,
    build_counts.pass_tests,
    build_counts.skip_tests,
  ]);

  return (
    <>
      {chartElements.some(slice => slice.value > 0) && (
        <div className="min-w-[400px]">
          <StatusChartMemoized
            type="chart"
            title={<FormattedMessage id="buildAccordion.testStatus" />}
            elements={chartElements}
          />
        </div>
      )}
    </>
  );
};

const BuildTestStatusChart = ({
  buildId,
}: {
  buildId: string;
}): JSX.Element => {
  const { data, status } = useBuildStatusCount(
    { buildId: buildId ?? '' },
    { enabled: !!buildId },
  );

  return (
    <QuerySwitcher data={data} status={status} skeletonClassname="h-[60px]">
      {data && <AccordBuildStatusChart buildCountsData={data} />}
    </QuerySwitcher>
  );
};

export const MemoizedBuildTestsChart = memo(BuildTestStatusChart);
