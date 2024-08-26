import { useCallback, useMemo, useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import BaseTable from '@/components/Table/BaseTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCell, TableRow } from '@/components/ui/table';
import { usePagination } from '@/hooks/usePagination';

import { useTestsByTreeAndCommitHash } from '@/api/TreeDetails';

import {
  TableFilter,
  possibleTestsTableFilter,
} from '@/types/tree/TreeDetails';

import TableStatusFilter from './TableStatusFilter';

const headerLabelIds: string[] = [
  'ID',
  'Status',
  'Path',
  'Compiler',
  'Architecture',
];

const ITEMS_PER_PAGE = 10;

export interface ITestsTable {
  treeId: string;
  isBootTable?: boolean;
}

const TestsTable = ({
  treeId,
  isBootTable = false,
}: ITestsTable): JSX.Element => {
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const intl = useIntl();
  const { origin, treeInfo, diffFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const { tableFilter: filterBy } = useSearch({
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
      });
    },
    [navigate, treeId],
  );

  const filteredData = useMemo(() => {
    if (filterBy === 'all') {
      return data?.tests;
    }
    return data?.tests.filter(test => test.status.toLowerCase() === filterBy);
  }, [data?.tests, filterBy]);

  const data_len = filteredData?.length || 0;

  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE, diffFilter, filterBy);

  const [selectedFilter, setSelectedFilter] = useState<TableFilter>('all');

  const headers = useMemo(() => {
    return headerLabelIds.map(labelId => <p key={labelId}>{labelId}</p>);
  }, []);

  const rows = useMemo(() => {
    if (!data || error) return <></>;

    if (filteredData?.length === 0) {
      return (
        <div className="flex h-8 items-center px-4">
          <FormattedMessage id="testDetails.noResults" />
        </div>
      );
    }

    return filteredData?.slice(startIndex, endIndex).map(test => (
      <TableRow onClick={() => onClickName(test.id)} key={test.id}>
        <TableCell>{test.id}</TableCell>
        <TableCell>{test.status}</TableCell>
        <TableCell>{test.path}</TableCell>
        <TableCell>{test.compiler}</TableCell>
        <TableCell>{test.architecture}</TableCell>
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

  const onClickFilter = useCallback(
    (filter: TableFilter) => {
      setSelectedFilter(filter);
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: filter,
          };
        },
      });
    },
    [navigate],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleTestsTableFilter[0],
        isSelected: selectedFilter === possibleTestsTableFilter[0],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.pass' }),
        value: possibleTestsTableFilter[5],
        isSelected: selectedFilter === possibleTestsTableFilter[5],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.fail' }),
        value: possibleTestsTableFilter[3],
        isSelected: selectedFilter === possibleTestsTableFilter[3],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.skip' }),
        value: possibleTestsTableFilter[6],
        isSelected: selectedFilter === possibleTestsTableFilter[6],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.done' }),
        value: possibleTestsTableFilter[1],
        isSelected: selectedFilter === possibleTestsTableFilter[1],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.error' }),
        value: possibleTestsTableFilter[2],
        isSelected: selectedFilter === possibleTestsTableFilter[2],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.miss' }),
        value: possibleTestsTableFilter[4],
        isSelected: selectedFilter === possibleTestsTableFilter[4],
      },
    ],
    [intl, selectedFilter],
  );

  if (error) return <FormattedMessage id="global.error" />;

  if (isLoading) return <FormattedMessage id="global.loading" />;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-row justify-between">
        <TableStatusFilter filters={filters} onClick={onClickFilter} />
        {tableInfoElement}
      </div>
      <BaseTable headers={headers}>{rows}</BaseTable>
      {tableInfoElement}
    </div>
  );
};

export default TestsTable;
