import { useIntl } from 'react-intl';

import {
  memo,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type JSX,
} from 'react';

import { z } from 'zod';

import { useMediaQuery } from '@mui/material';

import { useTheme } from '@mui/material/styles';

import {
  MdArrowBackIos,
  MdArrowForwardIos,
  MdFirstPage,
  MdLastPage,
} from 'react-icons/md';

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
import type {
  PaginatedCommitHistoryByTree,
  TreeDetailsRouteFrom,
} from '@/types/tree/TreeDetails';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { gitValues } from '@/components/Tooltip/CommitTagTooltip';

import { Button } from '@/components/ui/button';

const graphDisplaySize = 8;

const NUM_SELECTED_COMMITS = 6;

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
  commitsList?: string[];
  treeId?: string;
  startTimestampInSeconds?: number;
  endTimestampInSeconds?: number;
  onMarkClick: (commitHash: string, commitName?: string) => void;
  treeName?: string;
  treeUrlFrom?: TreeDetailsRouteFrom;
  buildsRelatedToFilteredTestsOnly?: boolean;
}

const CommitNavigationGraph = ({
  origin,
  currentPageTab,
  diffFilter,
  gitUrl,
  gitBranch,
  headCommitHash,
  commitsList,
  treeId,
  onMarkClick,
  endTimestampInSeconds,
  startTimestampInSeconds,
  treeName,
  treeUrlFrom,
  buildsRelatedToFilteredTestsOnly,
}: ICommitNavigationGraph): JSX.Element => {
  const { formatMessage } = useIntl();

  const reqFilter = mapFilterToReq(diffFilter);

  const [allCommits, setAllCommits] = useState<
    Map<string, PaginatedCommitHistoryByTree>
  >(new Map());
  const [visibleRange, setVisibleRange] = useState<[number, number]>([0, 0]);

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

  useEffect(() => {
    const commits = commitsList;
    if (!commits?.length) {
      setVisibleRange([0, 0]);
      return;
    }
    const start = commits.findIndex(c => c === headCommitHash);
    const last = Math.min(start + NUM_SELECTED_COMMITS, commits.length);
    setVisibleRange([start, last]);
  }, [commitsList, headCommitHash]);

  const commitHashes = useMemo(
    () =>
      commitsList
        ?.slice(visibleRange[0], visibleRange[1]) ?? [],
    [commitsList, visibleRange],
  );

  const missingCommitHashes = useMemo(
    () => commitHashes.filter(h => !allCommits.has(h)),
    [commitHashes, allCommits],
  );

  const { data, status, error, isLoading } = useCommitHistory({
    gitBranch: gitBranch ?? '',
    gitUrl: gitUrl ?? '',
    commitHash: missingCommitHashes,
    origin: origin,
    filter: reqFilter,
    endTimestampInSeconds,
    startTimestampInSeconds,
    treeName,
    treeUrlFrom,
    types,
    buildsRelatedToFilteredTestsOnly,
  });

  useEffect(() => {
    if (!data?.length) {
      return;
    }
    setAllCommits(prev => {
      let next: Map<string, PaginatedCommitHistoryByTree> | null = null;
      missingCommitHashes.forEach((commit, idx) => {
        const incoming = data[idx];
        if (incoming === undefined) {
          return;
        }
        if (prev.get(commit) !== incoming) {
          if (!next) {
            next = new Map(prev);
          }
          next.set(commit, incoming);
        }
      });
      return next ?? prev;
    });
  }, [data, missingCommitHashes]);

  const canGoNewer = visibleRange[0] > 0;
  const canGoOlder = visibleRange[1] < (commitsList?.length || 1) - 1;

  const goNewer = useCallback(() => {
    setVisibleRange(([start, end]) => [
      Math.max(start - NUM_SELECTED_COMMITS, 0),
      Math.max(end - NUM_SELECTED_COMMITS, NUM_SELECTED_COMMITS),
    ]);
  }, []);

  const goNewest = useCallback(() => {
    setVisibleRange(_ => [0, NUM_SELECTED_COMMITS] as [number, number]);
  }, []);

  const commitsLength = commitsList?.length ?? 0;

  const goOlder = useCallback(() => {
    const last = Math.max(commitsLength - 1, 0);
    setVisibleRange(
      ([start, end]) =>
        [
          Math.min(start + NUM_SELECTED_COMMITS, last - NUM_SELECTED_COMMITS),
          Math.min(end + NUM_SELECTED_COMMITS, last),
        ] as [number, number],
    );
  }, [commitsLength]);

  const goOldest = useCallback(() => {
    const last = Math.max(commitsLength - 1, 0);
    setVisibleRange(_ => [last - NUM_SELECTED_COMMITS, last]);
  }, [commitsLength]);

  const visibleCommits = commitHashes
    .map(commit => allCommits.get(commit))
    .reverse();

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

  // Transform the visible window data for the MUI LineChart
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

  // visibleCommits is already in chronological order (oldest first)
  visibleCommits.forEach(item => {
    if (!item) {
      return;
    }
    if (currentPageTab === 'global.builds') {
      const inconclusiveCount =
        item.builds.MISS +
        item.builds.SKIP +
        item.builds.ERROR +
        item.builds.DONE +
        item.builds.NULL;
      series[0].data?.push(item.builds.PASS);
      series[1].data?.push(item.builds.FAIL);
      series[2].data?.push(inconclusiveCount);
    }
    if (currentPageTab === 'global.boots') {
      const inconclusiveCount =
        item.boots.miss +
        item.boots.skip +
        item.boots.error +
        item.boots.done +
        item.boots.null;
      series[0].data?.push(item.boots.pass);
      series[1].data?.push(item.boots.fail);
      series[2].data?.push(inconclusiveCount);
    }
    if (currentPageTab === 'global.tests') {
      const inconclusiveCount =
        item.tests.miss +
        item.tests.skip +
        item.tests.error +
        item.tests.done +
        item.tests.null;
      series[0].data?.push(item.tests.pass);
      series[1].data?.push(item.tests.fail);
      series[2].data?.push(inconclusiveCount);
    }
    commitData.push({
      commitHash: item.git_commit_hash,
      commitName: item.git_commit_name,
      commitTags: item.git_commit_tags,
      earliestStartTime: item.earliest_start_time,
    });

    xAxisIndexes.push(commitData.length - 1);
  });

  // filter only selected, first and last commit
  const smallScreenTickFilter = (value: number, _: number): boolean =>
    value === 0 ||
    value === commitData.length - 1 ||
    commitData[value]?.commitHash === treeId;

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
          currentCommitData?.earliestStartTime ?? '-',
          true,
        );

        if (context.location === 'tooltip') {
          return (
            (currentCommitData?.commitName ??
              currentCommitData?.commitHash ??
              '') +
            ' - ' +
            currentCommitDateTime
          );
        }

        return `commitIndex-${value}`;
      },
      tickLabelInterval: tickLabelInterval,
    },
  ];

  const querySwitcherStatus = allCommits?.size > 0 ? 'success' : status;

  return (
    <QuerySwitcher
      status={querySwitcherStatus}
      data={visibleCommits}
      customError={
        <MemoizedSectionError
          isLoading={isLoading && allCommits.size === 0}
          errorMessage={error?.message}
          emptyLabel={'global.error'}
          forceErrorMessageUse
        />
      }
    >
      <BaseCard
        title={formatMessage({ id: messagesId.graphName })}
        content={
          <>
            <LineChart
              height={400}
              isLoading={isLoading}
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

                    const row = commitData[parsedPossibleIndex];
                    isCurrentCommit = treeId === row?.commitHash;

                    if (row) {
                      displayText = getChartXLabel(row);
                    }
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
                const row = commitData[commitIndex];
                if (row?.commitHash) {
                  onMarkClick(row.commitHash, row.commitName);
                }
              }}
            />
            <div className="mb-2 flex items-center justify-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={goOldest}
                disabled={!canGoOlder}
                title={formatMessage({ id: 'global.first' })}
              >
                <MdFirstPage className="text-blue" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={goOlder}
                disabled={!canGoOlder}
                title={formatMessage({ id: 'global.older' })}
              >
                <MdArrowBackIos className="text-blue" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={goNewer}
                disabled={!canGoNewer}
                title={formatMessage({ id: 'global.newer' })}
              >
                <MdArrowForwardIos className="text-blue" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={goNewest}
                disabled={!canGoNewer}
                title={formatMessage({ id: 'global.last' })}
              >
                <MdLastPage className="text-blue" />
              </Button>
            </div>
          </>
        }
      />
    </QuerySwitcher>
  );
};

export default memo(CommitNavigationGraph);
