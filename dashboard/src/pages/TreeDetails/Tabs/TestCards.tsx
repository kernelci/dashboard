import { FormattedMessage } from 'react-intl';

import { memo } from 'react';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import BaseCard, { IBaseCard } from '@/components/Cards/BaseCard';
import ListingItem from '@/components/ListingItem/ListingItem';
import { ArchCompilerStatus, TTreeTestsData } from '@/types/tree/TreeDetails';
import { TestStatus } from '@/components/Status/Status';

import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import StatusChartMemoized, {
  Colors,
  StatusChartValues,
} from '@/components/StatusChart/StatusCharts';
import { groupStatus } from '@/utils/status';

interface IConfigList extends Pick<TTreeTestsData, 'configStatusCounts'> {
  title: IBaseCard['title'];
}

const ConfigsList = ({
  configStatusCounts,
  title,
}: IConfigList): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {Object.keys(configStatusCounts).map(configName => {
            const { DONE, FAIL, ERROR, MISS, PASS, SKIP } =
              configStatusCounts[configName];
            return (
              <ListingItem
                hasBottomBorder
                key={configName}
                text={configName}
                leftIcon={
                  <TestStatus
                    done={DONE}
                    fail={FAIL}
                    error={ERROR}
                    miss={MISS}
                    pass={PASS}
                    skip={SKIP}
                    forceNumber={false}
                  />
                }
              />
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
export const MemoizedConfigList = memo(ConfigsList);

interface IPlatformsWithError
  extends Pick<TTreeTestsData, 'platformsWithError'> {
  title: IBaseCard['title'];
}

const PlatformsWithError = ({
  platformsWithError,
  title,
}: IPlatformsWithError): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {platformsWithError.map(platformWithErrorItem => {
            return (
              <ListingItem
                hasBottomBorder
                key={platformWithErrorItem}
                text={platformWithErrorItem}
                showNumber={false}
              />
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
export const MemoizedPlatformsWithError = memo(PlatformsWithError);

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
}

const ErrorsSummary = ({
  archCompilerErrors,
  title,
}: IErrorsSummary): JSX.Element => {
  const summaryHeaders = [
    <FormattedMessage key="treeDetail.arch" id="treeDetails.arch" />,
    <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
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
              <SummaryItem
                key={e.arch}
                arch={{
                  text: e.arch,
                }}
                leftIcon={
                  <TestStatus
                    forceNumber={false}
                    done={statusCounts.DONE}
                    fail={statusCounts.FAIL}
                    error={statusCounts.ERROR}
                    miss={statusCounts.MISS}
                    pass={statusCounts.PASS}
                    skip={statusCounts.SKIP}
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
    doneCount: statusCounts.DONE ?? 0,
    errorCount: statusCounts.ERROR ?? 0,
    failCount: statusCounts.FAIL ?? 0,
    missCount: statusCounts.MISS ?? 0,
    passCount: statusCounts.PASS ?? 0,
    skipCount: statusCounts.SKIP ?? 0,
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
