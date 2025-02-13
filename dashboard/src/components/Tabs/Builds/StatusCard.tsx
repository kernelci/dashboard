import { memo, useMemo, type JSX } from 'react';

import { useIntl } from 'react-intl';

import BaseCard from '@/components/Cards/BaseCard';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';
import type { TFilterObjectsKeys } from '@/types/general';
import type { IBuildsTab } from '@/pages/TreeDetails/Tabs/Build/BuildTab';

interface IStatusCard {
  buildsSummary?: IBuildsTab['buildsSummary'];
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}

const StatusCard = ({
  buildsSummary,
  toggleFilterBySection,
}: IStatusCard): JSX.Element => {
  const { formatMessage } = useIntl();

  const totalStatus = useMemo(() => {
    const invalid = buildsSummary?.invalid ?? 0;
    const valid = buildsSummary?.valid ?? 0;
    const nullables = buildsSummary?.null ?? 0;

    return invalid + valid + nullables;
  }, [buildsSummary]);

  if (!buildsSummary) {
    return <></>;
  }

  return (
    <BaseCard
      title={formatMessage({ id: 'buildTab.buildStatus' })}
      content={
        <StatusChartMemoized
          type="chart"
          pieCentralLabel={formatMessage({ id: 'global.executed' })}
          pieCentralDescription={<>{totalStatus}</>}
          onLegendClick={(value: string) => {
            toggleFilterBySection(value, 'buildStatus');
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

export const MemoizedStatusCard = memo(StatusCard);
