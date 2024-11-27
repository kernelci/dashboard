import { memo } from 'react';

import { useIntl } from 'react-intl';

import type { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import BaseCard from '../../Cards/BaseCard';
import StatusChartMemoized, { Colors } from '../../StatusChart/StatusCharts';

interface IStatusCard<T> {
  buildsSummary?: ITreeDetails['buildsSummary'];
  toggleFilterBySection: (value: string, filterSection: T) => void;
}

const StatusCard = <T,>({
  buildsSummary,
  toggleFilterBySection,
}: IStatusCard<T>): JSX.Element => {
  const { formatMessage } = useIntl();
  if (!buildsSummary) return <></>;

  return (
    <BaseCard
      title={formatMessage({ id: 'buildTab.buildStatus' })}
      content={
        <StatusChartMemoized
          type="chart"
          pieCentralLabel={formatMessage({ id: 'global.executed' })}
          pieCentralDescription={
            <>
              {(buildsSummary.invalid ?? 0) +
                (buildsSummary.valid ?? 0) +
                (buildsSummary.null ?? 0)}
            </>
          }
          onLegendClick={(value: string) => {
            toggleFilterBySection(value, 'buildStatus' as T);
          }}
          elements={[
            {
              value: buildsSummary.valid ?? 0,
              label: 'global.success',
              color: Colors.Green,
            },
            {
              value: buildsSummary.invalid ?? 0,
              label: 'global.failed',
              color: Colors.Red,
            },
            {
              value: buildsSummary.null ?? 0,
              label: 'global.inconclusive',
              color: Colors.Gray,
            },
          ]}
        />
      }
    />
  );
};

export const MemoizedStatusCard = memo(StatusCard) as <T>(
  props: IStatusCard<T>,
) => JSX.Element;
