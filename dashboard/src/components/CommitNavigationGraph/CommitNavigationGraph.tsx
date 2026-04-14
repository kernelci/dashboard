import { useIntl } from 'react-intl';

import {
  memo,
  useCallback,
  useEffect,
  useMemo,
  useRef,
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
const WINDOW_SIZE = 4;
const BACKEND_PAGE_SIZE = 6;

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

  // Buffer of all fetched commits (oldest first, i.e. chronological order)
  const [allCommits, setAllCommits] = useState<PaginatedCommitHistoryByTree[]>(
    [],
  );
  // Index of the rightmost visible commit in allCommits
  const [windowEnd, setWindowEnd] = useState<number>(-1);
  // Anchor commit hash for fetching older data
  const [fetchAnchor, setFetchAnchor] = useState<string | undefined>(undefined);
  // Whether the backend has no more older commits
  const [exhausted, setExhausted] = useState(false);

  // Reset everything when key props change
  const prevDepsRef = useRef({ headCommitHash, currentPageTab });
  useEffect(() => {
    const prev = prevDepsRef.current;
    if (
      prev.headCommitHash !== headCommitHash ||
      prev.currentPageTab !== currentPageTab
    ) {
      setAllCommits([]);
      setWindowEnd(-1);
      setFetchAnchor(undefined);
      setExhausted(false);
      prevDepsRef.current = { headCommitHash, currentPageTab };
    }
  }, [headCommitHash, currentPageTab]);

  const effectiveAnchor = fetchAnchor ?? headCommitHash ?? '';

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
    commitHash: effectiveAnchor,
    origin: origin,
    filter: reqFilter,
    endTimestampInSeconds,
    startTimestampInSeconds,
    treeName,
    treeUrlFrom,
    types,
    buildsRelatedToFilteredTestsOnly,
  });

  // Merge fetched data into the buffer when it arrives
  const lastMergedAnchorRef = useRef<string>('');
  useEffect(() => {
    if (!data || data.length === 0) {
      return;
    }
    if (lastMergedAnchorRef.current === effectiveAnchor) {
      return;
    }
    lastMergedAnchorRef.current = effectiveAnchor;

    if (data.length < BACKEND_PAGE_SIZE) {
      setExhausted(true);
    }

    // Data from API is newest-first; reverse to get chronological (oldest-first)
    const newCommits = [...data].reverse();

    setAllCommits(prev => {
      if (prev.length === 0) {
        return newCommits;
      }

      // Deduplicate: only prepend commits not already in the buffer
      const existingHashes = new Set(prev.map(c => c.git_commit_hash));
      const uniqueNew = newCommits.filter(
        c => !existingHashes.has(c.git_commit_hash),
      );

      if (uniqueNew.length === 0) {
        return prev;
      }

      const merged = [...uniqueNew, ...prev];
      // Shift window to account for prepended items
      setWindowEnd(w => (w === -1 ? merged.length - 1 : w + uniqueNew.length));
      return merged;
    });
  }, [data, effectiveAnchor]);

  // Initialize windowEnd when allCommits first populates
  useEffect(() => {
    if (allCommits.length > 0 && windowEnd === -1) {
      setWindowEnd(allCommits.length - 1);
    }
  }, [allCommits.length, windowEnd]);

  // Compute visible window
  const windowStart = Math.max(0, windowEnd - WINDOW_SIZE + 1);
  const visibleCommits = allCommits.slice(windowStart, windowEnd + 1);

  // Navigation
  const canGoNewer = windowEnd < allCommits.length - 1;
  const canGoOlder = windowStart > 0 || !exhausted;

  const goNewer = useCallback(() => {
    setWindowEnd(w => Math.min(w + 1, allCommits.length - 1));
  }, [allCommits.length]);

  const goNewest = useCallback(() => {
    setWindowEnd(allCommits.length - 1);
  }, [allCommits.length]);

  const goOlder = useCallback(() => {
    if (windowStart > 0) {
      setWindowEnd(w => w - 1);
    } else if (!exhausted && allCommits.length > 0) {
      // Need to fetch more: use the oldest known commit as anchor
      const oldestHash = allCommits[0].git_commit_hash;
      setFetchAnchor(oldestHash);
    }
  }, [windowStart, exhausted, allCommits]);

  const goOldest = useCallback(() => {
    if (exhausted) {
      setWindowEnd(WINDOW_SIZE - 1);
    } else if (allCommits.length > 0) {
      // Fetch more first, then we'll land at the start
      const oldestHash = allCommits[0].git_commit_hash;
      setFetchAnchor(oldestHash);
      setWindowEnd(WINDOW_SIZE - 1);
    }
  }, [exhausted, allCommits]);

  const displayableData = visibleCommits.length > 0 ? visibleCommits : null;

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
  visibleCommits.forEach((item, index) => {
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
          <>
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

                    displayText = getChartXLabel(
                      commitData[parsedPossibleIndex],
                    );
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
            <div className="mt-2 flex items-center justify-center gap-1">
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
