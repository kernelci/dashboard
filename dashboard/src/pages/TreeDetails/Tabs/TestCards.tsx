import { FormattedMessage } from 'react-intl';
import { memo, useMemo, type JSX } from 'react';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import type { IBaseCard } from '@/components/Cards/BaseCard';
import BaseCard from '@/components/Cards/BaseCard';
import ListingItem from '@/components/ListingItem/ListingItem';
import { GroupedTestStatus } from '@/components/Status/Status';
import type { TTreeTestsData } from '@/types/tree/TreeDetails';

import type { StatusChartValues } from '@/components/StatusChart/StatusCharts';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';
import { groupStatus } from '@/utils/status';
import type { ArchCompilerStatus } from '@/types/general';
import { ScrollArea } from '@/components/ui/scroll-area';

import { Badge } from '@/components/ui/badge';
import FilterLink from '@/components/Tabs/FilterLink';
import { DumbSummary, MemoizedSummaryItem } from '@/components/Tabs/Summary';

interface IConfigList extends Pick<TTreeTestsData, 'configStatusCounts'> {
  title: IBaseCard['title'];
  diffFilter: Record<string, Record<string, boolean>>;
}

const ConfigsList = ({
  configStatusCounts,
  title,
  diffFilter,
}: IConfigList): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {Object.keys(configStatusCounts).map(configName => {
            const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } =
              configStatusCounts[configName];
            return (
              <FilterLink
                key={configName}
                filterSection="configs"
                filterValue={configName}
                diffFilter={diffFilter}
              >
                <ListingItem
                  hasBottomBorder
                  key={configName}
                  text={configName}
                  leftIcon={
                    <GroupedTestStatus
                      done={DONE}
                      fail={FAIL}
                      error={ERROR}
                      miss={MISS}
                      pass={PASS}
                      skip={SKIP}
                      nullStatus={NULL}
                    />
                  }
                />
              </FilterLink>
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
export const MemoizedConfigList = memo(ConfigsList);

interface IHardwareTested
  extends Pick<TTreeTestsData, 'environmentCompatible'> {
  title: IBaseCard['title'];
  diffFilter: Record<string, Record<string, boolean>>;
}

const HardwareTested = ({
  environmentCompatible,
  title,
  diffFilter,
}: IHardwareTested): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <ScrollArea className="h-[350px]">
          <DumbListingContent>
            {Object.keys(environmentCompatible).map(hardwareTestedName => {
              const { DONE, FAIL, ERROR, MISS, PASS, SKIP, NULL } =
                environmentCompatible[hardwareTestedName];

              return (
                <FilterLink
                  key={hardwareTestedName}
                  filterSection="hardware"
                  filterValue={hardwareTestedName}
                  diffFilter={diffFilter}
                >
                  <ListingItem
                    hasBottomBorder
                    key={hardwareTestedName}
                    text={hardwareTestedName}
                    leftIcon={
                      <GroupedTestStatus
                        done={DONE}
                        fail={FAIL}
                        error={ERROR}
                        miss={MISS}
                        pass={PASS}
                        skip={SKIP}
                        nullStatus={NULL}
                      />
                    }
                  />
                </FilterLink>
              );
            })}
          </DumbListingContent>
        </ScrollArea>
      }
    />
  );
};
export const MemoizedHardwareTested = memo(HardwareTested);

interface IErrorCountList extends Pick<TTreeTestsData, 'errorMessageCounts'> {
  title: IBaseCard['title'];
}

const ErrorCountList = ({
  errorMessageCounts,
  title,
}: IErrorCountList): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {Object.keys(errorMessageCounts).map(errorMessage => {
            const currentErrorMessageCount = errorMessageCounts[errorMessage];
            return (
              <ListingItem
                key={errorMessage}
                text={errorMessage}
                errors={currentErrorMessageCount}
              />
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
export const MemoizedErrorCountList = memo(ErrorCountList);

interface IErrorsSummary {
  archCompilerErrors: ArchCompilerStatus[];
  title: IBaseCard['title'];
  diffFilter: Record<string, Record<string, boolean>>;
}

const ErrorsSummary = ({
  archCompilerErrors,
  title,
  diffFilter,
}: IErrorsSummary): JSX.Element => {
  const summaryHeaders = [
    <FormattedMessage key="global.arch" id="global.arch" />,
    <FormattedMessage key="global.compiler" id="global.compiler" />,
  ];

  return (
    <BaseCard
      title={title}
      content={
        <DumbSummary summaryHeaders={summaryHeaders}>
          {archCompilerErrors.map(e => {
            const statusCounts = e.status;
            const currentCompilers = [e.compiler];
            return (
              <MemoizedSummaryItem
                diffFilter={diffFilter}
                key={e.arch}
                arch={{
                  text: e.arch,
                }}
                leftIcon={
                  <GroupedTestStatus
                    forceNumber={false}
                    done={statusCounts.DONE}
                    fail={statusCounts.FAIL}
                    error={statusCounts.ERROR}
                    miss={statusCounts.MISS}
                    pass={statusCounts.PASS}
                    skip={statusCounts.SKIP}
                    nullStatus={statusCounts.NULL}
                  />
                }
                compilers={currentCompilers}
              />
            );
          })}
        </DumbSummary>
      }
    />
  );
};

export const MemoizedErrorsSummary = memo(ErrorsSummary);

interface IStatusChart extends Pick<TTreeTestsData, 'statusCounts'> {
  title: IBaseCard['title'];
}

const StatusChart = ({ statusCounts, title }: IStatusChart): JSX.Element => {
  const groupedStatusCounts = groupStatus({
    doneCount: statusCounts.DONE,
    errorCount: statusCounts.ERROR,
    failCount: statusCounts.FAIL,
    missCount: statusCounts.MISS,
    passCount: statusCounts.PASS,
    skipCount: statusCounts.SKIP,
    nullCount: statusCounts.NULL,
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

export const MemoizedStatusChart = memo(StatusChart);
