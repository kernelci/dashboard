import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import { TableRow, TableCell } from '../ui/table';

import { TreeTableBody } from '../../types/tree/Tree';

import BaseTable from './BaseTable';

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

const treeTableColumnsLabelId: MessagesKey[] = [
  'global.commit',
  'treeTable.patchset',
  'treeTable.build',
  'treeTable.test',
];

const TreeTableRow = (row: TreeTableBody): JSX.Element => {
  const backgroundClassName =
    'flex flex-row bg-lightGray w-fit h-fit p-1 rounded-lg';

  const navigate = useNavigate({ from: '/tree' });

  const navigateToTreeDetailPage = useCallback(() => {
    navigate({
      to: '/tree/$treeId',
      params: { treeId: row.id },
      search: {
        tableFilter: 'all',
        currentTreeDetailsTab: 'treeDetails.builds',
        diffFilter: {},
      },
    });
  }, [navigate, row.id]);

  return (
    <TableRow onClick={navigateToTreeDetailPage}>
      <TableCell>{sanitizeTableValue(row.commit)}</TableCell>
      <TableCell>{sanitizeTableValue(row.patchsetHash)}</TableCell>
      <TableCell>
        <div className={backgroundClassName}>
          {sanitizeTableValue(row.buildStatus)}
        </div>
      </TableCell>
      <TableCell>
        <div className={backgroundClassName}>
          {sanitizeTableValue(row.testStatus)}
        </div>
      </TableCell>
    </TableRow>
  );
};

const TreeTable = ({ treeTableRows }: ITreeTable): JSX.Element => {
  const treeTableBody = useMemo(() => {
    return treeTableRows.map((row: TreeTableBody) => (
      <TreeTableRow
        key={row.commit}
        commit={row.commit}
        patchsetHash={row.patchsetHash}
        buildStatus={row.buildStatus}
        testStatus={row.testStatus}
        id={row.id}
      />
    ));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [treeTableRows]);

  const treeTableHeaders = useMemo(() => {
    return treeTableColumnsLabelId.map(columnLabelId => (
      <FormattedMessage key={columnLabelId} id={columnLabelId} />
    ));
  }, []);

  return <BaseTable headers={treeTableHeaders} body={<>{treeTableBody}</>} />;
};

export default TreeTable;

const MAX_NUMBER_CHAR = 12;

const truncateTableValue = (value: string): string =>
  value.substring(0, MAX_NUMBER_CHAR) +
  (value.length > MAX_NUMBER_CHAR ? '...' : '');

const sanitizeTableValue = (value: string): string =>
  truncateTableValue(value) || '-';
