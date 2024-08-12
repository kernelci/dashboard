import { useCallback, useMemo } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import BaseTable from '@/components/Table/BaseTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCell, TableRow } from '@/components/ui/table';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { usePagination } from '@/hooks/usePagination';
import { formatDate } from '@/utils/utils';
import { MessagesKey } from '@/locales/messages';

import { useRevisionTest } from '@/api/TreeDetails';

const headerLabelIds: MessagesKey[] = [
  'global.origins',
  'global.name',
  'buildDetails.testResults',
  'buildDetails.startTime',
];

const testCellProps = [
  {
    name: 'pass_tests',
    colorClass: 'bg-lightGreen',
    tooltipLabelId: 'global.pass',
  },
  {
    name: 'done_tests',
    colorClass: 'bg-green',
    tooltipLabelId: 'global.done',
  },
  {
    name: 'fail_tests',
    colorClass: 'bg-lightRed',
    tooltipLabelId: 'global.failed',
  },
  {
    name: 'error_tests',
    colorClass: 'bg-red',
    tooltipLabelId: 'global.error',
  },
  {
    name: 'miss_tests',
    colorClass: 'bg-yellow',
    tooltipLabelId: 'global.missed',
  },
  {
    name: 'skip_tests',
    colorClass: 'bg-darkGray',
    tooltipLabelId: 'global.skiped',
  },
  {
    name: 'total_tests',
    colorClass: 'bg-darkGray2',
    tooltipLabelId: 'global.total',
  },
] as const;

const ITEMS_PER_PAGE = 10;

export interface ITestsTable {
  treeId: string;
  patchset?: string;
}

const TestsTable = ({ treeId, patchset = '' }: ITestsTable): JSX.Element => {
  const intl = useIntl();
  const { testPath } = useSearch({ from: '/tree/$treeId/' });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const { data, error } = useRevisionTest(treeId, patchset, testPath);
  const data_len = data?.length || 0;
  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE);

  const onClickName = useCallback(
    (e: React.MouseEvent<HTMLTableCellElement>) => {
      if (e.target instanceof HTMLTableCellElement) {
        const newTestPath = e.target.innerText;
        navigate({
          search: previousSearch => ({
            ...previousSearch,
            testPath: newTestPath,
          }),
        });
      }
    },
    [navigate],
  );

  const headers = useMemo(() => {
    return headerLabelIds.map(labelId => (
      <FormattedMessage key={labelId} id={labelId} />
    ));
  }, []);

  const rows = useMemo(() => {
    if (!data || error) return <></>;

    return data.slice(startIndex, endIndex).map(test => (
      <TableRow key={test.current_path}>
        <TableCell>{test.origins.join(', ')}</TableCell>
        <TableCell onClick={onClickName}>{test.current_path}</TableCell>
        <TableCell className="flex flex-row gap-1">
          {testCellProps.map(props => (
            <ColoredCircle
              key={test[props.name]}
              tooltipText={intl.formatMessage({ id: props.tooltipLabelId })}
              quantity={test[props.name]}
              backgroundClassName={props.colorClass}
            />
          ))}
        </TableCell>
        <TableCell>{formatDate(test.start_time)}</TableCell>
      </TableRow>
    ));
  }, [data, error, intl, onClickName, startIndex, endIndex]);

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

  return (
    <div className="flex flex-col gap-6">
      {tableInfoElement}
      <BaseTable headers={headers}>{rows}</BaseTable>
      {tableInfoElement}
    </div>
  );
};

export default TestsTable;
