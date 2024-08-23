import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

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
        <div className="flex flex-row gap-1">
          <ColoredCircle
            quantity={row.buildStatus.valid}
            backgroundClassName="bg-lightGreen"
          />
          <ColoredCircle
            quantity={row.buildStatus.invalid}
            backgroundClassName="bg-lightRed"
          />
          <ColoredCircle
            quantity={row.buildStatus.null}
            backgroundClassName="bg-lightGray"
          />
        </div>
      </TableCell>
      <TableCell>
        <div className="flex flex-row gap-1">
          <ColoredCircle
            quantity={row.testStatus.pass}
            backgroundClassName="bg-lightGreen"
          />
          <ColoredCircle
            quantity={row.testStatus.error}
            backgroundClassName="bg-lightRed"
          />
          <ColoredCircle
            quantity={row.testStatus.miss}
            backgroundClassName="bg-lightGray"
          />
          <ColoredCircle
            quantity={row.testStatus.fail}
            backgroundClassName="bg-yellow"
          />
          <ColoredCircle
            quantity={row.testStatus.done}
            backgroundClassName="bg-lightBlue"
          />
          <ColoredCircle
            quantity={row.testStatus.skip}
            backgroundClassName="bg-mediumGray"
          />
        </div>
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
