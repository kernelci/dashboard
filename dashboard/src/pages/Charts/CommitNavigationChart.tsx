import { useIntl } from 'react-intl';

import { z } from 'zod';

import { useMemo } from 'react';

import type { TLineChartProps } from '@/components/LineChart/LineChart';
import { LineChart } from '@/components/LineChart';
import type { MessagesKey } from '@/locales/messages';
import type { TTreeCommitHistoryResponse } from '@/types/tree/TreeDetails';
import { Colors } from '@/components/StatusChart/StatusCharts';
import { formatDate } from '@/utils/utils';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import BaseCard from '@/components/Cards/BaseCard';

type MessagesID = {
  graphName: MessagesKey;
  good: MessagesKey;
  bad: MessagesKey;
  mid: MessagesKey;
};

interface CommitNavigationChartProps {
  data: TTreeCommitHistoryResponse | undefined;
  currentDetailsTab: string;
  currentCommitHash: string;
  commitNavigate: (commitHash: string, commitName: string) => void;
  status: 'error' | 'success' | 'pending';
}

const graphDisplaySize = 7;

const CommitNavigationChart = ({
  data,
  currentDetailsTab,
  currentCommitHash,
  status,
  commitNavigate,
}: CommitNavigationChartProps): JSX.Element => {
  const { formatMessage } = useIntl();
  const displayableData = data ? data : null;

  const messagesId: MessagesID = useMemo(() => {
    switch (currentDetailsTab) {
      case 'boots':
        return {
          graphName: 'commitChart.bootsHistory',
          good: 'commitChart.successBoots',
          bad: 'commitChart.failedBoots',
          mid: 'commitChart.inconclusiveBoots',
        } as MessagesID;
      case 'tests':
        return {
          graphName: 'commitChart.testsHistory',
          good: 'commitChart.testsSuccess',
          bad: 'commitChart.testsFailed',
          mid: 'commitChart.testsInconclusive',
        } as MessagesID;
      default:
        return {
          graphName: 'commitChart.buildsHistory',
          good: 'commitChart.validBuilds',
          bad: 'commitChart.invalidBuilds',
          mid: 'commitChart.inconclusiveBuilds',
        } as MessagesID;
    }
  }, [currentDetailsTab]);

  // Transform the data to fit the format required by the MUI LineChart component
  const series: TLineChartProps['series'] = [
    {
      id: 'good',
      label: formatMessage({ id: messagesId.good }),
      data: [],
      color: Colors.Green,
    },
    {
      label: formatMessage({ id: messagesId.bad }),
      id: 'bad',
      data: [],
      color: Colors.Red,
    },
    {
      label: formatMessage({ id: messagesId.mid }),
      id: 'mid',
      data: [],
      color: Colors.Gray,
      highlightScope: {
        highlight: 'item',
      },
    },
  ];

  type TCommitValue = {
    commitHash: string;
    commitName?: string;
    earliestStartTime?: string;
  };

  const commitData: TCommitValue[] = [];
  const xAxisIndexes: number[] = [];
  // TODO Extract the magic code to outside the component
  data?.forEach((item, index) => {
    if (currentDetailsTab === 'builds') {
      series[0].data?.unshift(item.builds.valid_builds);
      series[1].data?.unshift(item.builds.invalid_builds);
      series[2].data?.unshift(item.builds.null_builds);
    }
    if (currentDetailsTab === 'boots') {
      const inconclusiveCount =
        item.boots_tests.miss_count +
        item.boots_tests.skip_count +
        item.boots_tests.error_count +
        item.boots_tests.done_count +
        item.boots_tests.null_count;
      series[0].data?.unshift(item.boots_tests.pass_count);
      series[1].data?.unshift(item.boots_tests.fail_count);
      series[2].data?.unshift(inconclusiveCount);
    }
    if (currentDetailsTab === 'tests') {
      const inconclusiveCount =
        item.non_boots_tests.miss_count +
        item.non_boots_tests.skip_count +
        item.non_boots_tests.error_count +
        item.non_boots_tests.done_count +
        item.non_boots_tests.null_count;
      series[0].data?.unshift(item.non_boots_tests.pass_count);
      series[1].data?.unshift(item.non_boots_tests.fail_count);
      series[2].data?.unshift(inconclusiveCount);
    }
    commitData.unshift({
      commitHash: item.git_commit_hash,
      commitName: item.git_commit_name,
      earliestStartTime: item.earliest_start_time,
    });
    xAxisIndexes.push(index);
  });

  const xAxis: TLineChartProps['xAxis'] = [
    {
      scaleType: 'point',
      min: 100,
      data: xAxisIndexes,
      valueFormatter: (value: number, context): string => {
        const currentCommitData = commitData[value];
        const currentCommitDateTime = formatDate(
          currentCommitData.earliestStartTime ?? '-',
          true,
        );

        if (context.location === 'tooltip') {
          return (
            (currentCommitData.commitName ?? currentCommitData.commitHash) +
            ' - ' +
            currentCommitDateTime
          );
        }

        return `commitIndex-${value}`;
      },
    },
  ];

  return (
    <QuerySwitcher status={status} data={displayableData}>
      <BaseCard
        title={formatMessage({ id: messagesId.graphName })}
        content={
          <LineChart
            xAxis={xAxis}
            series={series}
            slots={{
              axisTickLabel: chartTextProps => {
                let displayText = chartTextProps.text;
                const splitResult = chartTextProps.text.split('-');

                const possibleIdentifier = splitResult[0];

                let isCurrentCommit = false;
                if (possibleIdentifier === 'commitIndex') {
                  const possibleIndex = splitResult[1];
                  const possibleIndexNumber = parseInt(possibleIndex);
                  const parsedPossibleIndex = z
                    .number()
                    .catch(error => {
                      console.error('Error parsing index', error);
                      return 0;
                    })
                    .parse(possibleIndexNumber);

                  const name = commitData[parsedPossibleIndex].commitName;
                  isCurrentCommit =
                    currentCommitHash ===
                    commitData[parsedPossibleIndex].commitHash;
                  displayText = (
                    name ?? commitData[parsedPossibleIndex].commitHash
                  ).slice(0, graphDisplaySize);
                }

                return (
                  <>
                    {isCurrentCommit && (
                      <>
                        <polygon points="-5,-200 5,-200 0,-190" fill="blue" />
                        <line
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="-200"
                          stroke="blue"
                          strokeWidth="1.2"
                          strokeDasharray="5,5"
                        />
                      </>
                    )}

                    <text
                      className="MuiChartsAxis-tickLabel"
                      x="0"
                      y="9"
                      textAnchor="middle"
                      dominantBaseline="hanging"
                      style={{ fontSize: '0.9rem' }}
                    >
                      <tspan x="0" dy="0px" dominantBaseline="hanging">
                        {displayText}
                      </tspan>
                    </text>
                  </>
                );
              },
            }}
            onMarkClick={(_event, payload) => {
              const commitIndex = payload.dataIndex ?? 0;
              const commitHash = commitData[commitIndex].commitHash;
              const commitName = commitData[commitIndex].commitName;
              if (commitHash) commitNavigate(commitHash, commitName ?? '');
            }}
          />
        }
      />
    </QuerySwitcher>
  );
};

export default CommitNavigationChart;
