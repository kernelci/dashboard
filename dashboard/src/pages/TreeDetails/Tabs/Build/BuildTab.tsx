import { FormattedMessage, useIntl } from 'react-intl';

import { memo, useCallback, useMemo } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

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
import BaseCard from '@/components/Cards/BaseCard';

import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';

import { DesktopGrid, InnerMobileGrid, MobileGrid } from '../TabGrid';

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
              label: 'global.inconclusive',
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
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            treeDetailsData={treeDetailsData}
          />
          {/* TODO Kill the CardGroups component once and for all */}
          <CardsGroup cards={cards} />
        </div>
        <div>
          <CommitNavigationGraph />
          <MemoizedConfigsCard
            treeDetailsData={treeDetailsData}
            toggleFilterBySection={toggleFilterBySection}
          />
        </div>
      </DesktopGrid>
      <MobileGrid>
        <CommitNavigationGraph />
        <MemoizedStatusCard
          toggleFilterBySection={toggleFilterBySection}
          treeDetailsData={treeDetailsData}
        />
        <InnerMobileGrid>
          <CardsGroup cards={cards} />
          <MemoizedConfigsCard
            treeDetailsData={treeDetailsData}
            toggleFilterBySection={toggleFilterBySection}
          />
        </InnerMobileGrid>
      </MobileGrid>

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
