import { FormattedMessage, useIntl } from 'react-intl';

import { memo } from 'react';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import BaseCard, { IBaseCard } from '@/components/Cards/BaseCard';
import ListingItem from '@/components/ListingItem/ListingItem';
import { TTreeTestsData } from '@/types/tree/TreeDetails';
import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import StatusChartMemoized, {
  Colors,
  StatusChartValues,
} from '@/components/StatusChart/StatusCharts';
import { errorStatusSet } from '@/utils/constants/database';
import { ErrorStatus, Status } from '@/types/database';
import { LineChart, LineChartLabel } from '@/components/LineChart';

interface IConfigList extends Pick<TTreeTestsData, 'configCounts'> {
  title: IBaseCard['title'];
}

const ConfigsList = ({ configCounts, title }: IConfigList): JSX.Element => {
  return (
    <BaseCard
      title={title}
      content={
        <DumbListingContent>
          {Object.keys(configCounts).map(configName => {
            const currentConfigCount = configCounts[configName];
            return (
              <ListingItem
                hasBottomBorder
                key={configName}
                text={configName}
                success={currentConfigCount}
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
    'errorCountPerArchitecture' | 'compilersPerArchitecture'
  > {
  title: IBaseCard['title'];
}

const ErrorsSummary = ({
  errorCountPerArchitecture,
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
          {Object.keys(errorCountPerArchitecture).map(architecture => {
            const currentErrorCount = errorCountPerArchitecture[architecture];
            const currentCompilers = compilersPerArchitecture[architecture];
            return (
              <SummaryItem
                key={architecture}
                arch={{
                  text: architecture,
                  errors: currentErrorCount,
                }}
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
  const groupedStatus = {
    success: 0,
    fail: 0,
    skip: 0,
  };

  const statusKeys = Object.keys(statusCounts) as Status[];
  statusKeys.forEach(status => {
    if (errorStatusSet.has(status as ErrorStatus)) {
      groupedStatus.fail += statusCounts[status] ?? 0;
    } else if (status === 'SKIP') {
      groupedStatus.skip += 1;
    } else {
      groupedStatus.success += statusCounts[status] ?? 0;
    }
  });

  const chartElements = [
    {
      label: 'bootsTab.success',
      value: groupedStatus.success,
      color: Colors.Green,
    },
    {
      label: 'global.failed',
      value: groupedStatus.fail,
      color: Colors.Red,
    },
    {
      label: 'bootsTab.skip',
      value: groupedStatus.skip,
      color: Colors.Yellow,
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

interface ILineChartCard extends Pick<TTreeTestsData, 'testHistory'> {
  title: IBaseCard['title'];
}

const LineChartCard = ({ testHistory, title }: ILineChartCard): JSX.Element => {
  const { formatMessage } = useIntl();

  const allStartTimeStamps: number[] = [];
  const errorData: Array<number | null> = [];
  const skipData: Array<number | null> = [];
  const successData: Array<number | null> = [];
  let lastSkipData: null | number = null;
  let lastErrorData: null | number = null;
  let lastSuccessData: null | number = null;

  testHistory.forEach(boot => {
    allStartTimeStamps.push(new Date(boot.start_time).getTime());

    if (boot.status === 'SKIP') {
      lastSkipData = (lastSkipData ?? 0) + 1;
      skipData.push(lastSkipData);
      successData.push(null);
      errorData.push(null);
    } else if (errorStatusSet.has(boot.status as ErrorStatus)) {
      lastErrorData = (lastErrorData ?? 0) + 1;
      errorData.push(lastErrorData);
      successData.push(null);
      skipData.push(null);
    } else {
      lastSuccessData = (lastSuccessData ?? 0) + 1;
      successData.push(lastSuccessData);
      skipData.push(null);
      errorData.push(null);
    }
  });

  allStartTimeStamps.sort((a, b) => a - b);

  const lineChartSeries = [
    {
      color: Colors.Red,
      data: errorData,
      connectNulls: true,
      lastData: lastErrorData,
    },
    {
      color: Colors.Green,
      data: successData,
      connectNulls: true,
      lastData: lastSuccessData,
    },
    {
      color: Colors.Yellow,
      data: skipData,
      connectNulls: true,
      lastData: lastSkipData,
    },
  ];

  const filteredLineChartSeries = lineChartSeries.filter(series => {
    return series.data.some(data => data !== null);
  });
  return (
    <BaseCard
      title={title}
      content={
        <LineChart
          labels={
            <>
              {lastErrorData && (
                <LineChartLabel
                  text={formatMessage({ id: 'bootsTab.error' })}
                  backgroundColor="bg-red"
                />
              )}
              {lastSuccessData && (
                <LineChartLabel
                  text={formatMessage({ id: 'bootsTab.success' })}
                  backgroundColor="bg-green"
                />
              )}
              {lastSkipData && (
                <LineChartLabel
                  text={formatMessage({ id: 'bootsTab.skip' })}
                  backgroundColor="bg-yellow"
                />
              )}
            </>
          }
          xAxis={[
            {
              scaleType: 'time',
              data: allStartTimeStamps,
            },
          ]}
          series={[...filteredLineChartSeries]}
        />
      }
    />
  );
};

export const MemoizedLineChartCard = memo(LineChartCard);
