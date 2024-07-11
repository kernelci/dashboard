import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { TableRow, TableCell } from '../ui/table';

import { TreeTableBody } from '../../types/tree/Tree';

import BaseTable from './BaseTable';

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

const treeTableColumnsLabelId = [
  'treeTable.tree',
  'treeTable.branch',
  'treeTable.commit',
  'treeTable.build',
  'treeTable.test',
];

const TreeTableRow = (row: TreeTableBody): JSX.Element => {
  const backgroundClassName =
    'flex flex-row bg-lightGray w-fit h-fit p-1 rounded-lg';
  return (
    <TableRow>
      <TableCell>{row.name}</TableCell>
      <TableCell>{row.branch}</TableCell>
      <TableCell>{row.commit}</TableCell>
      <TableCell>
        <div className={backgroundClassName}>{row.buildStatus}</div>
      </TableCell>
      <TableCell>
        <div className={backgroundClassName}>{row.testStatus}</div>
      </TableCell>
    </TableRow>
  );
};

const TreeTable = ({ treeTableRows }: ITreeTable): JSX.Element => {
  const treeTableBody = useMemo(() => {
    return treeTableRows.map((row: TreeTableBody) => (
      <TreeTableRow
        key={row.commit}
        name={row.name}
        branch={row.branch}
        commit={row.commit}
        buildStatus={row.buildStatus}
        testStatus={row.testStatus}
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
