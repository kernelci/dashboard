import { useCallback, useMemo } from 'react';
import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import BaseTable from '@/components/Table/BaseTable';
import { TableInfo } from '@/components/Table/TableInfo';
import { TableCell, TableRow } from '@/components/ui/table';
import { usePagination } from '@/hooks/usePagination';

import { useTestsByCommitHash } from '@/api/TreeDetails';

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
}

const ImprovisedTestsTable = ({ treeId }: ITestsTable): JSX.Element => {
  const { data, error, isLoading } = useTestsByCommitHash(treeId);
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const data_len = data?.tests.length || 0;
  const { startIndex, endIndex, onClickGoForward, onClickGoBack } =
    usePagination(data_len, ITEMS_PER_PAGE);

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

  const headers = useMemo(() => {
    return headerLabelIds.map(labelId => <p key={labelId}>{labelId}</p>);
  }, []);

  const rows = useMemo(() => {
    if (!data || error) return <></>;

    return data.tests.slice(startIndex, endIndex).map(test => (
      <TableRow onClick={() => onClickName(test.id)} key={test.id}>
        <TableCell>{test.id}</TableCell>
        <TableCell>{test.status}</TableCell>
        <TableCell>{test.path}</TableCell>
        <TableCell>{test.compiler}</TableCell>
        <TableCell>{test.architecture}</TableCell>
      </TableRow>
    ));
  }, [data, error, startIndex, endIndex, onClickName]);

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

  if (error) return <FormattedMessage id="global.error" />;

  if (isLoading) return <FormattedMessage id="global.loading" />;

  return (
    <div className="flex flex-col gap-6">
      {tableInfoElement}
      <BaseTable headers={headers}>{rows}</BaseTable>
      {tableInfoElement}
    </div>
  );
};

export default ImprovisedTestsTable;
