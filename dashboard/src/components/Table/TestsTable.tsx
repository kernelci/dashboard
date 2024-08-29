import { useNavigate, useSearch } from '@tanstack/react-router';

import { useMemo } from 'react';

import { useIntl } from 'react-intl';

import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';

import { useTreeTest } from '@/api/TreeDetails';

import {
  TestsTableFilter,
  possibleTestsTableFilter,
} from '@/types/tree/TreeDetails';

import Accordion from '../Accordion/Accordion';

import TableStatusFilter from './TableStatusFilter';

const ITEMS_PER_PAGE = 10;

export interface ITestsTable {
  treeId: string;
}

const TestsTable = ({ treeId }: ITestsTable): JSX.Element => {
  const { testPath, treeInfo, origin, tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const { data } = useTreeTest(
    treeId,
    testPath,
    treeInfo.gitBranch ?? '',
    treeInfo.gitUrl ?? '',
    origin,
  );
  const data_len = data?.length || 0;
  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE);
  const intl = useIntl();

  const onClickFilter = (filter: TestsTableFilter): void => {
    navigate({
      search: previousParams => {
        return {
          ...previousParams,
          tableFilter: {
            bootsTable: previousParams.tableFilter.bootsTable,
            buildsTable: previousParams.tableFilter.buildsTable,
            testsTable: filter,
          },
        };
      },
    });
  };

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleTestsTableFilter[0],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[0],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.pass' }),
        value: possibleTestsTableFilter[5],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[5],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.fail' }),
        value: possibleTestsTableFilter[3],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[3],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.skip' }),
        value: possibleTestsTableFilter[6],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[6],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.done' }),
        value: possibleTestsTableFilter[1],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[1],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.error' }),
        value: possibleTestsTableFilter[2],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[2],
      },
      {
        label: intl.formatMessage({ id: 'testStatus.miss' }),
        value: possibleTestsTableFilter[4],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[4],
      },
    ],
    [intl, tableFilter.testsTable],
  );

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

  const filteredData = useMemo(() => {
    switch (tableFilter.testsTable) {
      case 'all':
        return data;
      case 'done':
        return data
          ?.filter(tests => tests.done_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[1],
            ),
          }));
      case 'error':
        return data
          ?.filter(tests => tests.done_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[2],
            ),
          }));
      case 'fail':
        return data
          ?.filter(tests => tests.fail_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[3],
            ),
          }));
      case 'miss':
        return data
          ?.filter(tests => tests.miss_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[4],
            ),
          }));
      case 'skip':
        return data
          ?.filter(tests => tests.skip_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[6],
            ),
          }));
      case 'pass':
        return data
          ?.filter(tests => tests.pass_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[5],
            ),
          }));
    }
  }, [tableFilter.testsTable, data]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-row justify-between">
        <TableStatusFilter
          onClickTest={(filter: TestsTableFilter) => onClickFilter(filter)}
          filters={filters}
        />
        {tableInfoElement}
      </div>
      <Accordion type="test" items={filteredData ?? []} />
      {tableInfoElement}
    </div>
  );
};

export default TestsTable;
