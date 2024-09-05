import { FormattedMessage } from 'react-intl';

import { memo } from 'react';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import BaseCard, { IBaseCard } from '@/components/Cards/BaseCard';
import ListingItem from '@/components/ListingItem/ListingItem';
import { TTreeTestsData } from '@/types/tree/TreeDetails';
import { TestStatus } from '@/components/Status/Status';

import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import StatusChartMemoized, {
  Colors,
  StatusChartValues,
} from '@/components/StatusChart/StatusCharts';

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

interface IErrorsSummary
  extends Pick<
    TTreeTestsData,
    'architectureStatusCounts' | 'compilersPerArchitecture'
  > {
  title: IBaseCard['title'];
}

const ErrorsSummary = ({
  architectureStatusCounts,
  compilersPerArchitecture,
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
          {Object.keys(architectureStatusCounts).map(architecture => {
            const statusCounts = architectureStatusCounts[architecture];
            const currentCompilers = compilersPerArchitecture[architecture];
            return (
              <SummaryItem
                key={architecture}
                arch={{
                  text: architecture,
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
  const chartElements = [
    {
      label: 'bootsTab.success',
      value: statusCounts['PASS'] ?? 0,
      color: Colors.Green,
    },
    {
      label: 'global.failed',
      value: statusCounts['FAIL'] ?? 0,
      color: Colors.Yellow,
    },
    {
      label: 'bootsTab.skip',
      value: statusCounts['SKIP'] ?? 0,
      color: Colors.DimGray,
    },
    {
      label: 'global.missed',
      value: statusCounts['MISS'] ?? 0,
      color: Colors.Gray,
    },
    {
      label: 'global.done',
      value: statusCounts['DONE'] ?? 0,
      color: Colors.Blue,
    },
    {
      label: 'bootsTab.error',
      value: statusCounts['ERROR'] ?? 0,
      color: Colors.Red,
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
