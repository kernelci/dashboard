import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { MdChevronRight } from 'react-icons/md';

import BaseTable from '@/components/Table/BaseTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCell, TableRow } from '@/components/ui/table';
import { usePagination } from '@/hooks/usePagination';

import { useTestsByTreeAndCommitHash } from '@/api/TreeDetails';

import {
  TestsTableFilter,
  possibleTestsTableFilter,
} from '@/types/tree/TreeDetails';

import TableStatusFilter from './TableStatusFilter';

const headerLabelIds: string[] = [
  'Path',
  'Status',
  'Start time',
  'Duration',
  '', //extra one to add the chevron icon
];

const ITEMS_PER_PAGE = 10;

export interface ITestsTable {
  treeId: string;
  isBootTable?: boolean;
}

const BootsTable = ({
  treeId,
  isBootTable = false,
}: ITestsTable): JSX.Element => {
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const intl = useIntl();
  const { origin, treeInfo, diffFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const { data, error, isLoading } = useTestsByTreeAndCommitHash(
    treeId,
    isBootTable,
    origin,
    treeInfo.gitUrl,
    treeInfo.gitBranch,
  );

  const onClickName = useCallback(
    (id: string) => {
      navigate({
        to: '/tree/$treeId/test/$testId',
        params: {
          treeId,
          testId: id,
        },
        search: s => s,
      });
    },
    [navigate, treeId],
  );

  const filteredData = useMemo(() => {
    const filterToApply = tableFilter.bootsTable;
    if (filterToApply === 'all') {
      return data?.tests;
    }
    return data?.tests.filter(
      test => test.status.toLowerCase() === filterToApply,
    );
  }, [data?.tests, tableFilter]);

  const data_len = filteredData?.length || 0;

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(
      data_len,
      ITEMS_PER_PAGE,
      tableFilter.bootsTable,
      tableFilter.testsTable,
      tableFilter.buildsTable,
      diffFilter,
    );

  const [bootsSelectedFilter, setBootsSelectedFilter] =
    useState<TestsTableFilter>(tableFilter.bootsTable);

  const headers = useMemo(() => {
    return headerLabelIds.map(labelId => <p key={labelId}>{labelId}</p>);
  }, []);

  const rows = useMemo(() => {
    if (!data || error) return <></>;

    if (filteredData?.length === 0) {
      return (
        <div className="flex h-8 items-center px-4">
          <FormattedMessage id="global.noResults" />
        </div>
      );
    }

    return filteredData?.slice(startIndex, endIndex).map(test => (
      <TableRow onClick={() => onClickName(test.id)} key={test.id}>
        <TableCell>{test.path}</TableCell>
        <TableCell>{test.status}</TableCell>
        <TableCell>{test.startTime ?? '-'}</TableCell>
        <TableCell>{test.duration ?? '-'}</TableCell>
        <TableCell>
          <MdChevronRight />
        </TableCell>
      </TableRow>
    ));
  }, [filteredData, data, error, startIndex, endIndex, onClickName]);

  const tableInfoElement = (
    <div className="flex flex-col items-end">
      <TableInfo
        startIndex={startIndex + 1}
        endIndex={endIndex}
        totalTrees={data_len}
        itemsPerPage={ITEMS_PER_PAGE}
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
            testsTable: previousParams.tableFilter.testsTable,
            buildsTable: previousParams.tableFilter.buildsTable,
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
        label: intl.formatMessage({ id: 'testStatus.pass' }),
        value: possibleTestsTableFilter[5],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[5]),
      },
      {
        label: intl.formatMessage({ id: 'testStatus.fail' }),
        value: possibleTestsTableFilter[3],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[3]),
      },
      {
        label: intl.formatMessage({ id: 'testStatus.skip' }),
        value: possibleTestsTableFilter[6],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[6]),
      },
      {
        label: intl.formatMessage({ id: 'testStatus.done' }),
        value: possibleTestsTableFilter[1],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[1]),
      },
      {
        label: intl.formatMessage({ id: 'testStatus.error' }),
        value: possibleTestsTableFilter[2],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[2]),
      },
      {
        label: intl.formatMessage({ id: 'testStatus.miss' }),
        value: possibleTestsTableFilter[4],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[4]),
      },
    ],
    [intl, checkIfFilterIsSelected],
  );

  if (error) return <FormattedMessage id="global.error" />;

  if (isLoading) return <FormattedMessage id="global.loading" />;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-row justify-between">
        <TableStatusFilter
          filters={filters}
          onClickTest={(filter: TestsTableFilter) => onClickFilter(filter)}
        />
        {tableInfoElement}
      </div>
      <BaseTable headers={headers}>{rows}</BaseTable>
      {tableInfoElement}
    </div>
  );
};

export default BootsTable;
