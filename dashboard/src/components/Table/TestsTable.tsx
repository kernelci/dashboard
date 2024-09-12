import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo } from 'react';

import { useIntl } from 'react-intl';

import { TableInfo } from '@/components/Table/TableInfo';
import { usePagination } from '@/hooks/usePagination';

import {
  TestHistory,
  TestsTableFilter,
  possibleTestsTableFilter,
} from '@/types/tree/TreeDetails';

import { getStatusGroup } from '@/utils/status';
import { TPathTests } from '@/types/general';

import Accordion from '../Accordion/Accordion';

import TableStatusFilter from './TableStatusFilter';

const ITEMS_PER_PAGE = 10;

export interface ITestsTable {
  testHistory: TestHistory[];
}

const TestsTable = ({ testHistory }: ITestsTable): JSX.Element => {
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const data = useMemo((): TPathTests[] => {
    type Groups = {
      [K: string]: TPathTests;
    };
    const groups: Groups = {};
    testHistory.forEach(e => {
      const parts = e.path.split('.', 1);
      const group = parts.length > 0 ? parts[0] : '-';
      if (!(group in groups)) {
        groups[group] = {
          done_tests: 0,
          fail_tests: 0,
          miss_tests: 0,
          pass_tests: 0,
          null_tests: 0,
          skip_tests: 0,
          error_tests: 0,
          total_tests: 0,
          path_group: group,
          individual_tests: [],
        };
      }
      groups[group].total_tests++;
      groups[group].individual_tests.push({
        duration: e.duration?.toString() ?? '',
        path: e.path,
        start_time: e.startTime,
        status: e.status,
      });
      switch (e.status) {
        case 'DONE':
          groups[group].done_tests++;
          break;
        case 'ERROR':
          groups[group].error_tests++;
          break;
        case 'FAIL':
          groups[group].fail_tests++;
          break;
        case 'MISS':
          groups[group].miss_tests++;
          break;
        case 'PASS':
          groups[group].pass_tests++;
          break;
        case 'SKIP':
          groups[group].skip_tests++;
          break;
      }
    });
    return Object.values(groups);
  }, [testHistory]);

  const data_len = data?.length || 0;
  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE);
  const intl = useIntl();

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
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
    },
    [navigate],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleTestsTableFilter[0],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[0],
      },
      {
        label: intl.formatMessage({ id: 'global.success' }),
        value: possibleTestsTableFilter[1],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[1],
      },
      {
        label: intl.formatMessage({ id: 'global.failed' }),
        value: possibleTestsTableFilter[2],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[2],
      },
      {
        label: intl.formatMessage({ id: 'global.inconclusive' }),
        value: possibleTestsTableFilter[3],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[3],
      },
    ],
    [intl, tableFilter.testsTable],
  );

  const tableInfoElement = (
    <div className="flex flex-col items-end">
      <TableInfo
        itemName="global.tests"
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
      case 'success':
        return data
          ?.filter(tests => tests.pass_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => getStatusGroup(t.status) === possibleTestsTableFilter[1],
            ),
          }));
      case 'failed':
        return data
          ?.filter(tests => tests.fail_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[2],
            ),
          }));
      case 'inconclusive':
        return data
          ?.filter(
            tests =>
              tests.done_tests > 0 ||
              tests.error_tests > 0 ||
              tests.miss_tests > 0 ||
              tests.skip_tests > 0 ||
              tests.null_tests > 0,
          )
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status.toLowerCase() === possibleTestsTableFilter[3],
            ),
          }));
    }
  }, [tableFilter.testsTable, data]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-row justify-between">
        <TableStatusFilter onClickTest={onClickFilter} filters={filters} />
        {tableInfoElement}
      </div>
      <Accordion type="test" items={filteredData ?? []} />
      {tableInfoElement}
    </div>
  );
};

export default TestsTable;
