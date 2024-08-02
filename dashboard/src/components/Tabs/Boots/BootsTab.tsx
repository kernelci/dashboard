import { FormattedMessage } from 'react-intl';

import { memo } from 'react';

import { useParams } from 'react-router-dom';

import { LineChart } from '@mui/x-charts/LineChart';

import { DumbListingContent } from '@/components/ListingContent/ListingContent';
import { useBootsTab } from '@/api/TreeDetails';
import BaseCard from '@/components/Cards/BaseCard';
import ListingItem from '@/components/ListingItem/ListingItem';
import { TBootsTabData } from '@/types/tree/TreeDetails';
import { DumbSummary, SummaryItem } from '@/components/Summary/Summary';
import StatusChartMemoized, {
  Colors,
  StatusChartValues,
} from '@/components/StatusChart/StatusCharts';
import { errorStatusSet } from '@/utils/constants/database';
import { ErrorStatus, Status } from '@/types/database';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

const ConfigsList = ({
  configCounts,
}: Pick<TBootsTabData, 'configCounts'>): JSX.Element => {
  return (
    <BaseCard
      title="Configs"
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
const MemoizedConfigList = memo(ConfigsList);

const PlatformsWithError = ({
  platformsWithError,
}: Pick<TBootsTabData, 'platformsWithError'>): JSX.Element => {
  return (
    <BaseCard
      title="Platforms failing at boot"
      content={
        <DumbListingContent>
          {platformsWithError.map(platformWithErrorItem => {
            return (
              <ListingItem
                hasBottomBorder
                key={platformWithErrorItem}
                text={platformWithErrorItem}
              />
            );
          })}
        </DumbListingContent>
      }
    />
  );
};
const MemoizedPlatformsWithError = memo(PlatformsWithError);

const ErrorCountList = ({
  errorMessageCounts,
}: Pick<TBootsTabData, 'errorMessageCounts'>): JSX.Element => {
  return (
    <BaseCard
      title={<>Fail</>}
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
const MemoizedErrorCountList = memo(ErrorCountList);

const ErrorsSummary = ({
  errorCountPerArchitecture,
  compilersPerArchitecture,
}: Pick<
  TBootsTabData,
  'errorCountPerArchitecture' | 'compilersPerArchitecture'
>): JSX.Element => {
  const summaryHeaders = [
    <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
    <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
  ];

  return (
    <BaseCard
      title="Errors Summary"
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

const MemoizedErrorsSummary = memo(ErrorsSummary);

const StatusChart = ({
  statusCounts,
}: Pick<TBootsTabData, 'statusCounts'>): JSX.Element => {
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
      label: <div>Success</div>,
      value: groupedStatus.success,
      color: Colors.Green,
    },
    {
      label: <div>Fail</div>,
      value: groupedStatus.fail,
      color: Colors.Red,
    },
    {
      label: <div>Skip</div>,
      value: groupedStatus.skip,
      color: Colors.Yellow,
    },
  ] satisfies StatusChartValues[];

  const filteredChartElements = chartElements.filter(chartElement => {
    return chartElement.value > 0;
  });

  return (
    <BaseCard
      title="Boot Status"
      content={
        <StatusChartMemoized type="chart" elements={filteredChartElements} />
      }
    />
  );
};

const StatusChartMemo = memo(StatusChart);

interface ILineChartLabel {
  text: string;
  backgroundColor: string;
}

//TODO Extract Line Chart to its own component

const LineChartLabel = ({
  text,
  backgroundColor,
}: ILineChartLabel): JSX.Element => {
  return (
    <div className="flex items-center gap-2 pr-6 font-medium text-gray-700">
      <ColoredCircle
        className="h-3 w-3"
        backgroundClassName={backgroundColor}
      />
      <span>{text}</span>
    </div>
  );
};

const LineChartCard = ({
  bootHistory,
}: Pick<TBootsTabData, 'bootHistory'>): JSX.Element => {
  const allStartTimeStamps: number[] = [];
  const errorData: Array<number | null> = [];
  const skipData: Array<number | null> = [];
  const successData: Array<number | null> = [];
  let lastSkipData: null | number = null;
  let lastErrorData: null | number = null;
  let lastSuccessData: null | number = null;

  bootHistory.forEach(boot => {
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
      title="Boot history"
      content={
        <div className="px-4">
          <div className="mb-0 mt-3 flex justify-end gap-2">
            {lastErrorData && (
              <LineChartLabel text="Error" backgroundColor="bg-red" />
            )}
            {lastSuccessData && (
              <LineChartLabel text="Success" backgroundColor="bg-green" />
            )}
            {lastSkipData && (
              <LineChartLabel text="Skip" backgroundColor="bg-yellow" />
            )}
          </div>
          <LineChart
            className="w-full bg-red"
            xAxis={[
              {
                scaleType: 'time',
                data: allStartTimeStamps,
              },
            ]}
            series={filteredLineChartSeries}
            height={300}
          />
        </div>
      }
    />
  );
};

const MemoizedLineChartCard = memo(LineChartCard);

const BootsTab = (): JSX.Element => {
  const { treeId } = useParams();
  const { isLoading, data, error } = useBootsTab(treeId ?? '');

  if (error || !treeId) {
    return <div>Error</div>;
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!data) return <div />;

  if (data.bootHistory.length < 1) {
    return (
      <BaseCard
        title="Info"
        content={
          <p className="p-4 text-[1.3rem] text-darkGray">
            ℹ️ There is no boot test data available for this tree
          </p>
        }
      />
    );
  }

  return (
    <div className="flex flex-col gap-8 pt-4">
      <div className="md:columns-2">
        <StatusChartMemo statusCounts={data.statusCounts} />
        <MemoizedConfigList configCounts={data.configCounts} />
        <MemoizedErrorsSummary
          errorCountPerArchitecture={data.errorCountPerArchitecture}
          compilersPerArchitecture={data.compilersPerArchitecture}
        />
        <MemoizedLineChartCard bootHistory={data.bootHistory} />
        <MemoizedPlatformsWithError
          platformsWithError={data.platformsWithError}
        />
        <MemoizedErrorCountList errorMessageCounts={data.errorMessageCounts} />
      </div>
    </div>
  );
};

export default BootsTab;
