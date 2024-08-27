import { FormattedMessage, useIntl } from 'react-intl';

import { useCallback, useMemo, useState } from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import CardsGroup from '@/components/CardsGroup/CardsGroup';
import { Colors, IStatusChart } from '@/components/StatusChart/StatusCharts';
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

interface BuildTab {
  treeDetailsData?: ITreeDetails;
}

const BuildTab = ({ treeDetailsData }: BuildTab): JSX.Element => {
  const { tableFilter: filterBy } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({
    from: '/tree/$treeId',
  });
  const { diffFilter } = useSearch({ from: '/tree/$treeId/' });

  const [selectedFilter, setSelectedFilter] =
    useState<BuildsTableFilter>('all');

  const accordionContent = useMemo(() => {
    return treeDetailsData?.builds.map(row => ({
      accordionData: {
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
      },
    }));
  }, [treeDetailsData?.builds]);

  const filteredContent =
    filterBy.buildsTable === 'error'
      ? accordionContent?.filter(
          row =>
            row.accordionData.buildErrors && row.accordionData.buildErrors > 0,
        )
      : filterBy.buildsTable === 'success'
        ? accordionContent?.filter(
            row =>
              row.accordionData.status && row.accordionData.status === 'valid',
          )
        : accordionContent;

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(
      filteredContent?.length ?? 0,
      ITEMS_PER_PAGE,
      filterBy.bootsTable,
      filterBy.testsTable,
      filterBy.buildsTable,
      diffFilter,
    );
  const intl = useIntl();
  const cards = useMemo(() => {
    const toggleFilterBySection = (
      filterSectionKey: string,
      filterSection: TFilterObjectsKeys,
    ): void => {
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
    };

    return [
      {
        title: <FormattedMessage id="treeDetails.buildStatus" />,
        key: 'buildStatus',
        type: 'chart',
        onLegendClick: (value: string) => {
          toggleFilterBySection(value, 'status');
        },
        pieCentralDescription: (
          <>
            {(treeDetailsData?.buildsSummary.invalid ?? 0) +
              (treeDetailsData?.buildsSummary.valid ?? 0) +
              (treeDetailsData?.buildsSummary.null ?? 0)}
          </>
        ),
        pieCentralLabel: intl.formatMessage({ id: 'treeDetails.executed' }),
        elements: [
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
        ],
      } as IStatusChart & { key: string },
      {
        items: treeDetailsData?.configs ?? [],
        title: <FormattedMessage id="treeDetails.configs" />,
        key: 'configs',
        type: 'listing',
        onClickItem: (value: string) => {
          toggleFilterBySection(value, 'configs');
        },
      } as IListingContent & { key: string },
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
      } as ISummary & { key: string },
    ];
  }, [
    intl,
    navigate,
    treeDetailsData?.archs,
    treeDetailsData?.buildsSummary.invalid,
    treeDetailsData?.buildsSummary.null,
    treeDetailsData?.buildsSummary.valid,
    treeDetailsData?.configs,
  ]);

  const onClickFilter = useCallback(
    (type: BuildsTableFilter) => {
      setSelectedFilter(type);
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
      <CardsGroup cards={cards} />
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
