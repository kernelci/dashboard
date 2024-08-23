import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import { BuildStatus, TestStatus } from '@/components/Status/Status';

import { TableRow, TableCell } from '../ui/table';

import { TreeTableBody, zOrigin } from '../../types/tree/Tree';

import BaseTable from './BaseTable';
import { sanitizeTableValue } from './tableUtils';

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

const treeTableColumnsLabelId: MessagesKey[] = [
  'treeTable.tree',
  'treeTable.branch',
  'treeTable.commitTag',
  'filter.treeURL',
  'global.date',
  'treeTable.build',
  'treeTable.bootStatus',
  'treeTable.test',
];

const TreeTableRow = (row: TreeTableBody): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const navigate = useNavigate({ from: '/tree' });

  const navigateToTreeDetailPage = useCallback(() => {
    navigate({
      to: '/tree/$treeId',
      params: { treeId: row.id },
      search: {
        tableFilter: 'all',
        origin: origin,
        currentTreeDetailsTab: 'treeDetails.builds',
        diffFilter: {},
        treeInfo: {
          gitUrl: row.url,
          gitBranch: row.branch,
          treeName: row.tree_names[0],
          commitName: row.commitName,
        },
      },
    });
  }, [
    navigate,
    row.id,
    origin,
    row.url,
    row.branch,
    row.tree_names,
    row.commitName,
  ]);

  return (
    <TableRow onClick={navigateToTreeDetailPage}>
      <TableCell>
        {sanitizeTableValue(row.tree_names.join(', '), false)}
      </TableCell>
      <TableCell>{sanitizeTableValue(row.branch, false)}</TableCell>
      <TableCell>
        {sanitizeTableValue(
          row.commitName !== '' ? row.commitName : row.commitHash,
        )}
      </TableCell>
      <TableCell>{sanitizeTableValue(row.url, false)}</TableCell>
      <TableCell>{sanitizeTableValue(row.date.split('T')[0] ?? '')}</TableCell>
      <TableCell>
        <BuildStatus
          valid={row.buildStatus.valid}
          invalid={row.buildStatus.invalid}
          unknown={row.buildStatus.null}
        />
      </TableCell>
      <TableCell>
        <TestStatus
          pass={row.bootStatus.pass}
          skip={row.bootStatus.skip}
          fail={row.bootStatus.fail}
          miss={row.bootStatus.miss}
          done={row.bootStatus.done}
          error={row.bootStatus.error}
        />
      </TableCell>
      <TableCell>
        <TestStatus
          pass={row.testStatus.pass}
          skip={row.testStatus.skip}
          fail={row.testStatus.fail}
          miss={row.testStatus.miss}
          done={row.testStatus.done}
          error={row.testStatus.error}
        />
      </TableCell>
    </TableRow>
  );
};

const TreeTable = ({ treeTableRows }: ITreeTable): JSX.Element => {
  const treeTableBody = useMemo(() => {
    return treeTableRows.map((row: TreeTableBody) => (
      <TreeTableRow
        key={row.commitHash}
        commitHash={row.commitHash}
        patchsetHash={row.patchsetHash}
        buildStatus={row.buildStatus}
        testStatus={row.testStatus}
        tree_names={row.tree_names}
        id={row.id}
        branch={row.branch}
        date={row.date}
        url={row.url}
        commitName={row.commitName}
        bootStatus={row.bootStatus}
      />
    ));
  }, [treeTableRows]);

  const treeTableHeaders = useMemo(() => {
    return treeTableColumnsLabelId.map(columnLabelId => (
      <FormattedMessage key={columnLabelId} id={columnLabelId} />
    ));
  }, []);

  return <BaseTable headers={treeTableHeaders} body={<>{treeTableBody}</>} />;
};

export default TreeTable;
