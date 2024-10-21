import { memo, ReactElement, useCallback, useMemo, useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';
import { LinkProps, useNavigate, useSearch } from '@tanstack/react-router';

import { MdChevronRight } from 'react-icons/md';

import BaseTable from '@/components/Table/BaseTable';
import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCellWithLink, TableBody, TableRow } from '@/components/ui/table';
import { usePagination } from '@/hooks/usePagination';

import {
  TTestByCommitHashResponse,
  TestByCommitHash,
  TestHistory,
  TestsTableFilter,
  possibleTestsTableFilter,
} from '@/types/tree/TreeDetails';

import HeaderWithInfo from '@/pages/TreeDetails/Tabs/HeaderWithInfo';

import { getStatusGroup } from '@/utils/status';

import { ItemsPerPageValues } from '@/utils/constants/general';

// import { DataTableDemo } from '@/pages/TreeDetails/Tabs/Build/datatable';

import TableStatusFilter from './TableStatusFilter';

const headerLabelOrElement: (string | ReactElement)[] = [
  'Path',
  <HeaderWithInfo
    key={'status'}
    labelId="global.status"
    tooltipId="bootsTab.statusTooltip"
  />,
  'Start time',
  'Duration',
  '', //extra one to add the chevron icon
];

const headerElements = headerLabelOrElement.map(item =>
  typeof item === 'string' ? <p key={item}>{item}</p> : item,
);

export interface ITestsTable {
  treeId: string;
  testHistory: TestHistory[];
}

const BootsTable = ({ treeId, testHistory }: ITestsTable): JSX.Element => {
  const [itemsPerPage, setItemsPerPage] = useState(ItemsPerPageValues[0]);

  const navigate = useNavigate({ from: '/tree/$treeId' });
  const intl = useIntl();
  const { diffFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const data = useMemo(
    (): TTestByCommitHashResponse => ({
      tests: testHistory.map(
        (e): TestByCommitHash => ({
          duration: e.duration?.toString() ?? '',
          id: e.id,
          path: e.path,
          startTime: e.startTime,
          status: e.status,
        }),
      ),
    }),
    [testHistory],
  );

  const filteredData = useMemo(() => {
    const filterToApply = tableFilter.bootsTable;
    if (filterToApply === 'all') {
      return data?.tests;
    }
    return data?.tests.filter(test => {
      return getStatusGroup(test.status) === filterToApply;
    });
  }, [data?.tests, tableFilter]);

  const data_len = filteredData?.length || 0;

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(
      data_len,
      itemsPerPage,
      tableFilter.bootsTable,
      tableFilter.testsTable,
      tableFilter.buildsTable,
      diffFilter,
    );

  const [bootsSelectedFilter, setBootsSelectedFilter] =
    useState<TestsTableFilter>(tableFilter.bootsTable);

  const TestTableRow = ({ test }: { test: TestByCommitHash }): JSX.Element => {
    const linkProps: LinkProps = useMemo(
      () => ({
        to: '/tree/$treeId/test/$testId',
        params: {
          treeId,
          testId: test.id,
        },
        search: s => s,
      }),
      [test],
    );

    return (
      <TableRow key={test.id}>
        <TableCellWithLink linkProps={linkProps}>{test.path}</TableCellWithLink>
        <TableCellWithLink linkProps={linkProps}>
          {test.status}
        </TableCellWithLink>
        <TableCellWithLink linkProps={linkProps}>
          <TooltipDateTime
            dateTime={test.startTime}
            lineBreak={true}
            showLabelTime={true}
            showLabelTZ={true}
          />
        </TableCellWithLink>
        <TableCellWithLink linkProps={linkProps}>
          {test.duration ?? '-'}
        </TableCellWithLink>
        <TableCellWithLink linkProps={linkProps}>
          <MdChevronRight />
        </TableCellWithLink>
      </TableRow>
    );
  };

  const MemoizedTestTableRow = memo(TestTableRow);

  const rows = useMemo(() => {
    if (!data) return <></>;

    if (filteredData?.length === 0) {
      return (
        <div className="flex h-8 items-center px-4">
          <FormattedMessage id="global.noResults" />
        </div>
      );
    }

    return filteredData
      ?.slice(startIndex, endIndex)
      .map(test => <MemoizedTestTableRow key={test.id} test={test} />);
  }, [filteredData, data, startIndex, endIndex, MemoizedTestTableRow]);

  const tableInfoElement = (
    <div className="flex flex-col items-end">
      <TableInfo
        itemName="global.boots"
        startIndex={startIndex + 1}
        endIndex={endIndex}
        totalTrees={data_len}
        itemsPerPageValues={ItemsPerPageValues}
        itemsPerPageSelected={itemsPerPage}
        onChangeItemsPerPage={setItemsPerPage}
        onClickBack={onClickGoBack}
        onClickForward={onClickGoForward}
      />
    </div>
  );

  const onClickFilter = (filter: TestsTableFilter): void => {
    setBootsSelectedFilter(filter);
    navigate({
      search: previousParams => {
        return {
          ...previousParams,
          tableFilter: {
            ...previousParams.tableFilter,
            bootsTable: filter,
          },
        };
      },
    });
  };

  const checkIfFilterIsSelected = useCallback(
    (filter: TestsTableFilter): boolean => {
      return bootsSelectedFilter === filter;
    },
    [bootsSelectedFilter],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleTestsTableFilter[0],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[0]),
      },
      {
        label: intl.formatMessage({ id: 'global.success' }),
        value: possibleTestsTableFilter[1],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[1]),
      },
      {
        label: intl.formatMessage({ id: 'global.failed' }),
        value: possibleTestsTableFilter[2],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[2]),
      },
      {
        label: intl.formatMessage({ id: 'global.inconclusive' }),
        value: possibleTestsTableFilter[3],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[3]),
      },
    ],
    [intl, checkIfFilterIsSelected],
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-row justify-between">
        <TableStatusFilter
          filters={filters}
          onClickTest={(filter: TestsTableFilter) => onClickFilter(filter)}
        />
        {tableInfoElement}
      </div>
      <BaseTable headers={headerElements}>
        <TableBody>{rows}</TableBody>
      </BaseTable>
      {tableInfoElement}
      {/* <DataTableDemo></DataTableDemo> */}
    </div>
  );
};

export default BootsTable;
