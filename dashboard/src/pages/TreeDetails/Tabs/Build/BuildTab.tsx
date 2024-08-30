import { FormattedMessage, useIntl } from 'react-intl';

import { memo, useCallback, useMemo } from 'react';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { z } from 'zod';

import CardsGroup from '@/components/CardsGroup/CardsGroup';
import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';
import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';
import Accordion from '@/components/Accordion/Accordion';
import { IListingContent } from '@/components/ListingContent/ListingContent';
import { ISummary } from '@/components/Summary/Summary';

import {
  BuildsTableFilter,
  possibleBuildsTableFilter,
  TFilterObjectsKeys,
} from '@/types/tree/TreeDetails';
import { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';
import TableStatusFilter from '@/components/Table/TableStatusFilter';
import { LineChart } from '@/components/LineChart';
import BaseCard from '@/components/Cards/BaseCard';
import { useTreeCommitHistory } from '@/api/TreeDetails';
import { TLineChartProps } from '@/components/LineChart/LineChart';

interface BuildTab {
  treeDetailsData?: ITreeDetails;
}

const StatusCard = ({
  treeDetailsData,
  toggleFilterBySection,
}: {
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
  treeDetailsData?: ITreeDetails;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  return (
    <BaseCard
      title={formatMessage({ id: 'treeDetails.buildStatus' })}
      content={
        <StatusChartMemoized
          type="chart"
          pieCentralLabel={formatMessage({ id: 'treeDetails.executed' })}
          pieCentralDescription={
            <>
              {(treeDetailsData?.buildsSummary.invalid ?? 0) +
                (treeDetailsData?.buildsSummary.valid ?? 0) +
                (treeDetailsData?.buildsSummary.null ?? 0)}
            </>
          }
          onLegendClick={(value: string) => {
            toggleFilterBySection(value, 'buildStatus');
          }}
          elements={[
            {
              value: treeDetailsData?.buildsSummary.valid ?? 0,
              label: 'treeDetails.success',
              color: Colors.Green,
            },
            {
              value: treeDetailsData?.buildsSummary.invalid ?? 0,
              label: 'treeDetails.failed',
              color: Colors.Red,
            },
            {
              value: treeDetailsData?.buildsSummary.null ?? 0,
              label: 'treeDetails.unknown',
              color: Colors.Gray,
            },
          ]}
        />
      }
    />
  );
};

const MemoizedStatusCard = memo(StatusCard);

const ConfigsCard = ({
  treeDetailsData,
  toggleFilterBySection,
}: {
  treeDetailsData?: ITreeDetails;
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}): JSX.Element => {
  return (
    <CardsGroup
      cards={[
        {
          items: treeDetailsData?.configs ?? [],
          title: <FormattedMessage id="treeDetails.configs" />,
          key: 'configs',
          type: 'listing',
          onClickItem: (value: string) => {
            toggleFilterBySection(value, 'configs');
          },
        } as IListingContent & { key: string },
      ]}
    />
  );
};
const MemoizedConfigsCard = memo(ConfigsCard);

const graphDisplaySize = 7;
const LineChartNavigationCard = (): JSX.Element => {
  const { formatMessage } = useIntl();
  const {
    origin,
    treeInfo: { gitUrl, gitBranch, headCommitHash },
  } = useSearch({ from: '/tree/$treeId/' });

  const { treeId } = useParams({
    from: '/tree/$treeId/',
  });

  const navigate = useNavigate({
    from: '/tree/$treeId',
  });

  const { data, isLoading } = useTreeCommitHistory(
    {
      gitBranch: gitBranch ?? '',
      gitUrl: gitUrl ?? '',
      commitHash: headCommitHash ?? '',
      origin: origin,
    },
    {
      enabled: !!gitBranch && !!gitUrl,
    },
  );

  if (isLoading) {
    return <div>{formatMessage({ id: 'global.loading' })}</div>;
  }

  if (!data || !headCommitHash) {
    return <div>{formatMessage({ id: 'global.noDataAvailable' })}</div>;
  }

  // Transform the data to fit the format required by the MUI LineChart component
  const series: TLineChartProps['series'] = [
    {
      id: 'valid_builds',
      label: formatMessage({ id: 'treeDetails.validBuilds' }),
      data: [],
      color: Colors.Green,
    },
    {
      label: formatMessage({ id: 'treeDetails.invalidBuilds' }),
      id: 'invalid_builds',
      data: [],
      color: Colors.Red,
    },
    {
      label: formatMessage({
        id: 'treeDetails.nullBuilds',
      }),
      id: 'null_builds',
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
  };

  const commitData: TCommitValue[] = [];
  const xAxisIndexes: number[] = [];
  data.forEach((item, index) => {
    series[0].data?.unshift(item.valid_builds);
    series[1].data?.unshift(item.invalid_builds);
    series[2].data?.unshift(item.null_builds);
    commitData.unshift({
      commitHash: item.git_commit_hash,
      commitName: item.git_commit_name,
    });
    xAxisIndexes.push(index);
  });

  const xAxis: TLineChartProps['xAxis'] = [
    {
      scaleType: 'point',
      min: 100,
      data: xAxisIndexes,
      valueFormatter: (value: number, context): string => {
        if (context.location == 'tooltip') {
          const currentCommitData = commitData[value];
          return currentCommitData.commitName ?? currentCommitData.commitHash;
        }

        return `commitIndex-${value}`;
      },
    },
  ];
  return (
    <BaseCard
      title={formatMessage({ id: 'buildDetails.buildsHistory' })}
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
                  treeId === commitData[parsedPossibleIndex].commitHash;
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
            if (commitHash) {
              navigate({
                to: '/tree/$treeId',
                params: {
                  treeId: commitHash,
                },
                search: previousParams => {
                  previousParams;

                  return {
                    ...previousParams,
                    treeInfo: {
                      ...previousParams.treeInfo,
                      commitName: commitName,
                      commitHash: commitHash,
                    },
                  };
                },
              });
            }
          }}
        />
      }
    />
  );
};

export const MemoizedLineChartCard = memo(LineChartNavigationCard);

const BuildTab = ({ treeDetailsData }: BuildTab): JSX.Element => {
  const { tableFilter: filterBy } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({
    from: '/tree/$treeId',
  });
  const {
    diffFilter,
    tableFilter: { buildsTable: selectedFilter },
  } = useSearch({ from: '/tree/$treeId/' });

  const intl = useIntl();

  const accordionContent = useMemo(() => {
    return treeDetailsData?.builds.map(row => ({
      ...row,
      config: row.config ?? '-',
      compiler: row.compiler ?? '-',
      buildTime: row.buildTime ? (
        <span>
          {typeof row.buildTime === 'number'
            ? Math.floor(row.buildTime) + ' '
            : row.buildTime}
          <FormattedMessage id="global.seconds" />
        </span>
      ) : (
        '-'
      ),
      date: row.date?.split('T')[0],
      testStatus: {
        failTests: row.testStatus?.failTests ?? 0,
        errorTests: row.testStatus?.errorTests ?? 0,
        passTests: row.testStatus?.passTests ?? 0,
        skipTests: row.testStatus?.skipTests ?? 0,
        doneTests: row.testStatus?.doneTests ?? 0,
        missTests: row.testStatus?.missTests ?? 0,
      },
    }));
  }, [treeDetailsData?.builds]);

  const filteredContent =
    filterBy.buildsTable === 'all'
      ? accordionContent
      : accordionContent?.filter(
          row => row.status && row.status === filterBy.buildsTable,
        );

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(
      filteredContent?.length ?? 0,
      ITEMS_PER_PAGE,
      filterBy.bootsTable,
      filterBy.testsTable,
      filterBy.buildsTable,
      diffFilter,
    );

  const toggleFilterBySection = useCallback(
    (filterSectionKey: string, filterSection: TFilterObjectsKeys): void => {
      navigate({
        search: previousParams => {
          const { diffFilter: currentDiffFilter } = previousParams;
          const newFilter = structuredClone(currentDiffFilter);
          // This seems redundant but we do this to keep the pointer to newFilter[filterSection]
          newFilter[filterSection] = newFilter[filterSection] ?? {};
          const configs = newFilter[filterSection];
          if (configs[filterSectionKey]) {
            delete configs[filterSectionKey];
          } else {
            configs[filterSectionKey] = true;
          }

          return {
            ...previousParams,
            diffFilter: newFilter,
          };
        },
      });
    },
    [navigate],
  );

  const cards = useMemo(() => {
    return [
      {
        summaryBody: treeDetailsData?.archs ?? [],
        title: <FormattedMessage id="treeDetails.summary" />,
        key: 'summary',
        summaryHeaders: [
          <FormattedMessage key="treeDetails.arch" id="treeDetails.arch" />,
          <FormattedMessage
            key="treeDetails.compiler"
            id="treeDetails.compiler"
          />,
        ],
        type: 'summary',
        onClickKey: (key: string) => {
          toggleFilterBySection(key, 'archs');
        },
        onClickCompiler: compiler => {
          toggleFilterBySection(compiler, 'compilers');
        },
      } as ISummary & { key: string },
    ];
  }, [toggleFilterBySection, treeDetailsData?.archs]);

  const onClickFilter = useCallback(
    (type: BuildsTableFilter) => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              buildsTable: type,
              bootsTable: previousParams.tableFilter.bootsTable,
              testsTable: previousParams.tableFilter.testsTable,
            },
          };
        },
      });
    },
    [navigate],
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <div className="hidden grid-cols-2 gap-4 min-[1652px]:grid">
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            treeDetailsData={treeDetailsData}
          />
          {/* TODO Kill the CardGroups component once and for all */}
          <CardsGroup cards={cards} />
        </div>
        <div>
          <MemoizedLineChartCard />
          <MemoizedConfigsCard
            treeDetailsData={treeDetailsData}
            toggleFilterBySection={toggleFilterBySection}
          />
        </div>
      </div>
      <div className="min-[1652px]:hidden">
        <MemoizedLineChartCard />
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          treeDetailsData={treeDetailsData}
        />
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <CardsGroup cards={cards} />
          <MemoizedConfigsCard
            treeDetailsData={treeDetailsData}
            toggleFilterBySection={toggleFilterBySection}
          />
        </div>
      </div>

      {filteredContent && (
        <div className="flex flex-col gap-4">
          <div className="text-lg">
            <FormattedMessage id="treeDetails.builds" />
          </div>
          <div className="flex flex-row justify-between">
            <TableStatusFilter
              onClickBuild={(filter: BuildsTableFilter) =>
                onClickFilter(filter)
              }
              filters={[
                {
                  label: intl.formatMessage({ id: 'global.all' }),
                  value: possibleBuildsTableFilter[2],
                  isSelected: selectedFilter === possibleBuildsTableFilter[2],
                },
                {
                  label: intl.formatMessage({ id: 'global.successful' }),
                  value: possibleBuildsTableFilter[1],
                  isSelected: selectedFilter === possibleBuildsTableFilter[1],
                },
                {
                  label: intl.formatMessage({ id: 'global.errors' }),
                  value: possibleBuildsTableFilter[0],
                  isSelected: selectedFilter === possibleBuildsTableFilter[0],
                },
                {
                  label: intl.formatMessage({ id: 'global.unknown' }),
                  value: possibleBuildsTableFilter[3],
                  isSelected: selectedFilter === possibleBuildsTableFilter[3],
                },
              ]}
            />
            <TableInfo
              startIndex={startIndex + 1}
              endIndex={endIndex}
              totalTrees={filteredContent?.length ?? 0}
              itemsPerPage={ITEMS_PER_PAGE}
              onClickBack={onClickGoBack}
              onClickForward={onClickGoForward}
            />
          </div>
          <Accordion
            type="build"
            items={filteredContent.slice(startIndex, endIndex)}
          />
          <div className="flex justify-end">
            <TableInfo
              startIndex={startIndex + 1}
              endIndex={endIndex}
              totalTrees={filteredContent?.length ?? 0}
              itemsPerPage={ITEMS_PER_PAGE}
              onClickBack={onClickGoBack}
              onClickForward={onClickGoForward}
            />
          </div>
        </div>
      )}
    </div>
  );
};

const ITEMS_PER_PAGE = 10;

export default BuildTab;
