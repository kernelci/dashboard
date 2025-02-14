import { useIntl } from 'react-intl';

import { memo, useMemo } from 'react';

import type { LineSeriesType } from '@mui/x-charts';
import {
  ChartsAxisHighlight,
  ChartsLegend,
  ChartsReferenceLine,
  ChartsTooltip,
  ChartsXAxis,
  ChartsYAxis,
  LineHighlightPlot,
  LinePlot,
  MarkPlot,
  ResponsiveChartContainer,
} from '@mui/x-charts';

import { Colors } from '@/components/StatusChart/StatusCharts';
import BaseCard from '@/components/Cards/BaseCard';
import type { TLineChartProps } from '@/components/LineChart/LineChart';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { MessagesKey } from '@/locales/messages';
import { formatDate } from '@/utils/utils';
import { mapFilterToReq } from '@/components/Tabs/Filters';
import { useCommitHistory } from '@/api/commitHistory';
import type { TFilter } from '@/types/general';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { gitValues } from '@/components/Tooltip/CommitTagTooltip';

const graphDisplaySize = 8;

const getChartXLabel = ({
  commitTags,
  commitHash,
  commitName,
}: gitValues): string => {
  let content = commitHash ?? commitName ?? '';
  if (commitTags && commitTags.length > 0) {
    content = commitTags[0];

    if (content.length > graphDisplaySize) {
      content = `...${content.slice(-graphDisplaySize)}`;
    }
  } else {
    content = `${content.slice(0, graphDisplaySize)}`;
  }

  return content;
};

interface ICommitNavigationGraph {
  origin: string;
  currentPageTab: string;
  diffFilter: TFilter;
  gitUrl?: string;
  gitBranch?: string;
  headCommitHash?: string;
  treeId?: string;
  startTimestampInSeconds?: number;
  endTimestampInSeconds?: number;
  onMarkClick: (commitHash: string, commitName?: string) => void;
}

const CommitNavigationGraph = ({
  origin,
  currentPageTab,
  diffFilter,
  gitUrl,
  gitBranch,
  headCommitHash,
  treeId,
  onMarkClick,
  endTimestampInSeconds,
  startTimestampInSeconds,
}: ICommitNavigationGraph): JSX.Element => {
  const { formatMessage } = useIntl();

  const reqFilter = mapFilterToReq(diffFilter);

  const { data, status, error, isLoading } = useCommitHistory({
    gitBranch: gitBranch ?? '',
    gitUrl: gitUrl ?? '',
    commitHash: headCommitHash ?? '',
    origin: origin,
    filter: reqFilter,
    endTimestampInSeconds,
    startTimestampInSeconds,
  });

  const displayableData = data ? data : null;

  type MessagesID = {
    graphName: MessagesKey;
    good: MessagesKey;
    bad: MessagesKey;
    mid: MessagesKey;
  };

  const messagesId: MessagesID = useMemo(() => {
    switch (currentPageTab) {
      case 'global.boots':
        return {
          graphName: 'treeDetails.bootsHistory',
          good: 'treeDetails.successBoots',
          bad: 'treeDetails.failedBoots',
          mid: 'treeDetails.inconclusiveBoots',
        } as MessagesID;
      case 'global.tests':
        return {
          graphName: 'treeDetails.testsHistory',
          good: 'treeDetails.testsSuccess',
          bad: 'treeDetails.testsFailed',
          mid: 'treeDetails.testsInconclusive',
        } as MessagesID;
      default:
        return {
          graphName: 'treeDetails.buildsHistory',
          good: 'treeDetails.validBuilds',
          bad: 'treeDetails.invalidBuilds',
          mid: 'treeDetails.inconclusiveBuilds',
        } as MessagesID;
    }
  }, [currentPageTab]);

  // Transform the data to fit the format required by the MUI LineChart component
  const series: LineSeriesType[] = [
    {
      id: 'good',
      label: formatMessage({ id: messagesId.good }),
      data: [],
      color: Colors.Green,
      type: 'line',
    },
    {
      label: formatMessage({ id: messagesId.bad }),
      id: 'bad',
      data: [],
      color: Colors.Red,
      type: 'line',
    },
    {
      label: formatMessage({ id: messagesId.mid }),
      id: 'mid',
      data: [],
      color: Colors.Gray,
      highlightScope: {
        highlight: 'item',
      },
      type: 'line',
    },
  ];

  type TCommitValue = {
    commitHash: string;
    commitName?: string;
    commitTags?: string[];
    earliestStartTime?: string;
  };

  const commitData: TCommitValue[] = [];
  const xAxisIndexes: number[] = [];
  // TODO Extract the magic code to outside the component
  data?.forEach((item, index) => {
    if (currentPageTab === 'global.builds') {
      series[0].data?.unshift(item.builds.valid);
      series[1].data?.unshift(item.builds.invalid);
      series[2].data?.unshift(item.builds.null);
    }
    if (currentPageTab === 'global.boots') {
      const inconclusiveCount =
        item.boots.miss +
        item.boots.skip +
        item.boots.error +
        item.boots.done +
        item.boots.null;
      series[0].data?.unshift(item.boots.pass);
      series[1].data?.unshift(item.boots.fail);
      series[2].data?.unshift(inconclusiveCount);
    }
    if (currentPageTab === 'global.tests') {
      const inconclusiveCount =
        item.tests.miss +
        item.tests.skip +
        item.tests.error +
        item.tests.done +
        item.tests.null;
      series[0].data?.unshift(item.tests.pass);
      series[1].data?.unshift(item.tests.fail);
      series[2].data?.unshift(inconclusiveCount);
    }
    commitData.unshift({
      commitHash: item.git_commit_hash,
      commitName: item.git_commit_name,
      commitTags: item.git_commit_tags,
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

        return getChartXLabel({
          commitTags: currentCommitData.commitTags,
          commitHash: currentCommitData.commitHash,
          commitName: currentCommitData.commitName,
        });
      },
    },
  ];

  return (
    <QuerySwitcher
      status={status}
      data={displayableData}
      customError={
        <MemoizedSectionError
          isLoading={isLoading}
          errorMessage={error?.message}
          emptyLabel={'global.error'}
        />
      }
    >
      <BaseCard
        title={formatMessage({ id: messagesId.graphName })}
        content={
          <ResponsiveChartContainer xAxis={xAxis} series={series} height={300}>
            <LinePlot />
            <ChartsXAxis tickLabelStyle={{ fontSize: 15 }} />
            <ChartsYAxis tickLabelStyle={{ fontSize: 15 }} />
            <ChartsReferenceLine
              x={3} // This should be the currentCommit position
              lineStyle={{
                strokeDasharray: '5,5',
                stroke: 'blue',
                strokeWidth: 2,
              }}
              labelStyle={{ fontSize: '10' }}
              labelAlign="start"
            />
            <MarkPlot
              onItemClick={(_event, payload) => {
                const commitIndex = payload.dataIndex ?? 0;
                const commitHash = commitData[commitIndex].commitHash;
                const commitName = commitData[commitIndex].commitName;
                if (commitHash) {
                  onMarkClick(commitHash, commitName);
                }
              }}
            />
            <ChartsLegend />
            <ChartsAxisHighlight x="line" />
            <ChartsTooltip trigger="axis" />
            <LineHighlightPlot />
          </ResponsiveChartContainer>
        }
      />
    </QuerySwitcher>
  );
};

export default memo(CommitNavigationGraph);
