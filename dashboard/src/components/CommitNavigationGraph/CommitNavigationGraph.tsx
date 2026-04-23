import { useIntl } from 'react-intl';

import { memo, useMemo, type JSX } from 'react';

import { z } from 'zod';

import { useMediaQuery } from '@mui/material';

import { useTheme } from '@mui/material/styles';

import { Colors } from '@/components/StatusChart/StatusCharts';
import { LineChart } from '@/components/LineChart';
import BaseCard from '@/components/Cards/BaseCard';
import type { TLineChartProps } from '@/components/LineChart/LineChart';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { MessagesKey } from '@/locales/messages';
import { formatDate } from '@/utils/utils';
import { mapFilterToReq } from '@/components/Tabs/Filters';
import { useCommitHistory } from '@/api/commitHistory';
import type { TFilter, TreeEntityTypes } from '@/types/general';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { gitValues } from '@/components/Tooltip/CommitTagTooltip';
import type { TreeDetailsRouteFrom } from '@/types/tree/TreeDetails';

const graphDisplaySize = 8;

export const getChartXLabel = ({
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
  commitsList: string[];
  startTimestampInSeconds?: number;
  endTimestampInSeconds?: number;
  onMarkClick: (commitHash: string, commitName?: string) => void;
  treeName?: string;
  treeUrlFrom?: TreeDetailsRouteFrom;
  buildsRelatedToFilteredTestsOnly?: boolean;
}

const selectedCommits = (
  allCommits: string[] | undefined,
  headCommit: string | undefined,
): string[] => {
  allCommits = allCommits || [];
  headCommit = headCommit || '';
  const NUM_SELECTED_COMMITS = 6;
  const headIndex = allCommits.findIndex(x => x === headCommit);
  if (headIndex < 0) {
    return [];
  }
  return allCommits.slice(headIndex, headIndex + NUM_SELECTED_COMMITS);
};

const CommitNavigationGraph = ({
  origin,
  currentPageTab,
  diffFilter,
  gitUrl,
  gitBranch,
  headCommitHash,
  treeId,
  commitsList,
  onMarkClick,
  endTimestampInSeconds,
  startTimestampInSeconds,
  treeName,
  treeUrlFrom,
  buildsRelatedToFilteredTestsOnly,
}: ICommitNavigationGraph): JSX.Element => {
  const { formatMessage } = useIntl();

  const reqFilter = mapFilterToReq(diffFilter);

  const types: TreeEntityTypes[] = useMemo(() => {
    switch (currentPageTab) {
      case 'global.builds':
        return ['builds'];
      case 'global.boots':
        return ['boots'];
      case 'global.tests':
        return ['tests'];
      default:
        return ['builds'];
    }
  }, [currentPageTab]);

  const { data, status, error, isLoading } = useCommitHistory({
    gitBranch: gitBranch ?? '',
    gitUrl: gitUrl ?? '',
    commitHash: selectedCommits(commitsList, headCommitHash),
    origin: origin,
    filter: reqFilter,
    endTimestampInSeconds,
    startTimestampInSeconds,
    treeName,
    treeUrlFrom,
    types,
    buildsRelatedToFilteredTestsOnly,
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

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

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
    commitTags?: string[];
    earliestStartTime?: string;
  };

  const commitData: TCommitValue[] = [];
  const xAxisIndexes: number[] = [];
  // TODO Extract the magic code to outside the component
  data?.forEach((item, index) => {
    if (currentPageTab === 'global.builds') {
      const inconclusiveCount =
        item.builds.MISS +
        item.builds.SKIP +
        item.builds.ERROR +
        item.builds.DONE +
        item.builds.NULL;
      series[0].data?.unshift(item.builds.PASS);
      series[1].data?.unshift(item.builds.FAIL);
      series[2].data?.unshift(inconclusiveCount);
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

  // filter only selected, first and last commit
  const smallScreenTickFilter = (value: number, _: number): boolean =>
    value === 0 ||
    value === commitData.length - 1 ||
    commitData[value].commitHash === treeId;

  // tickLabelInterval can be set to auto, or to a custom filter
  const tickLabelInterval = isSmallScreen ? smallScreenTickFilter : 'auto';

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
      tickLabelInterval: tickLabelInterval,
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
          forceErrorMessageUse
        />
      }
    >
      <BaseCard
        title={formatMessage({ id: messagesId.graphName })}
        content={
          <LineChart
            height={400}
            margin={{ top: 100 }}
            xAxis={xAxis}
            series={series}
            sx={{
              '& .MuiChartsAxis-directionY .MuiChartsAxis-tickContainer:first-of-type':
                {
                  display: 'none', // hides first tick on y axis (avoiding text colision)
                },
            }}
            slotProps={{
              legend: {
                itemGap: 2,
                position: { vertical: 'top', horizontal: 'middle' },
              },
            }}
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
                    .catch(e => {
                      console.error('Error parsing index', e);
                      return 0;
                    })
                    .parse(possibleIndexNumber);

                  isCurrentCommit =
                    treeId === commitData[parsedPossibleIndex].commitHash;

                  displayText = getChartXLabel(commitData[parsedPossibleIndex]);
                }

                return (
                  <>
                    {isCurrentCommit && (
                      <>
                        <polygon points="-5,-250 5,-250 0,-240" fill="blue" />
                        <line
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="-250"
                          stroke="blue"
                          strokeWidth="2"
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
              if (commitHash) {
                onMarkClick(commitHash, commitName);
              }
            }}
          />
        }
      />
    </QuerySwitcher>
  );
};

export default memo(CommitNavigationGraph);
