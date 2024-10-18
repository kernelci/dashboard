import { FormattedMessage, useIntl } from 'react-intl';

import { memo, useCallback, useMemo, useState } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import StatusChartMemoized, {
  Colors,
} from '@/components/StatusChart/StatusCharts';
import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';
import Accordion from '@/components/Accordion/Accordion';
import { DumbListingContent } from '@/components/ListingContent/ListingContent';

import {
  BuildsTableFilter,
  possibleBuildsTableFilter,
  TFilterObjectsKeys,
} from '@/types/tree/TreeDetails';
import { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';
import TableStatusFilter from '@/components/Table/TableStatusFilter';
import BaseCard from '@/components/Cards/BaseCard';

import CommitNavigationGraph from '@/pages/TreeDetails/Tabs/CommitNavigationGraph';
import { MemoizedErrorsSummaryBuild } from '@/pages/TreeDetails/Tabs/BuildCards';

import { BuildStatus } from '@/components/Status/Status';

import ListingItem from '@/components/ListingItem/ListingItem';

import { ItemsPerPageValues } from '@/utils/constants/general';

import { MemoizedIssuesList } from '@/pages/TreeDetails/Tabs/TestCards';

import FilterLink from '@/pages/TreeDetails/TreeDetailsFilterLink';

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
}: {
  treeDetailsData?: ITreeDetails;
  toggleFilterBySection: (
    value: string,
    filterSection: TFilterObjectsKeys,
  ) => void;
}): JSX.Element => {
  const content = useMemo(() => {
    return (
      <DumbListingContent>
        {treeDetailsData?.configs.map((item, i) => (
          <FilterLink key={i} filterSection="configs" filterValue={item.text}>
            <ListingItem
              text={item.text}
              leftIcon={
                <BuildStatus
                  valid={item.success}
                  invalid={item.errors}
                  unknown={item.unknown}
                />
              }
            />
          </FilterLink>
        ))}
      </DumbListingContent>
    );
  }, [treeDetailsData?.configs]);

  return (
    <BaseCard
      title={<FormattedMessage id="treeDetails.configs" />}
      content={content}
    />
  );
};
const MemoizedConfigsCard = memo(ConfigsCard);

const BuildTab = ({ treeDetailsData }: BuildTab): JSX.Element => {
  const [itemsPerPage, setItemsPerPage] = useState(ItemsPerPageValues[0]);

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
      date: row.date,
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
      itemsPerPage,
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

  const tableInfoElement = (
    <TableInfo
      itemName="global.build"
      startIndex={startIndex + 1}
      endIndex={endIndex}
      totalTrees={filteredContent?.length ?? 0}
      itemsPerPageValues={ItemsPerPageValues}
      itemsPerPageSelected={itemsPerPage}
      onChangeItemsPerPage={setItemsPerPage}
      onClickBack={onClickGoBack}
      onClickForward={onClickGoForward}
    />
  );

  return (
    <div className="flex flex-col gap-8 pt-4">
      <DesktopGrid>
        <div>
          <MemoizedStatusCard
            toggleFilterBySection={toggleFilterBySection}
            treeDetailsData={treeDetailsData}
          />
          <MemoizedErrorsSummaryBuild
            summaryBody={treeDetailsData?.archs ?? []}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedIssuesList
            title={<FormattedMessage id="global.issues" />}
            issues={treeDetailsData?.issues || []}
          />
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
          <MemoizedErrorsSummaryBuild
            summaryBody={treeDetailsData?.archs ?? []}
            toggleFilterBySection={toggleFilterBySection}
          />
          <MemoizedConfigsCard
            treeDetailsData={treeDetailsData}
            toggleFilterBySection={toggleFilterBySection}
          />
        </InnerMobileGrid>
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={treeDetailsData?.issues || []}
        />
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
                  label: intl.formatMessage({ id: 'global.failed' }),
                  value: possibleBuildsTableFilter[0],
                  isSelected: selectedFilter === possibleBuildsTableFilter[0],
                },
                {
                  label: intl.formatMessage({ id: 'global.inconclusive' }),
                  value: possibleBuildsTableFilter[3],
                  isSelected: selectedFilter === possibleBuildsTableFilter[3],
                },
              ]}
            />
            {tableInfoElement}
          </div>
          <Accordion
            type="build"
            items={filteredContent.slice(startIndex, endIndex)}
          />
          <div className="flex justify-end">{tableInfoElement}</div>
        </div>
      )}
    </div>
  );
};

export default BuildTab;
