import { useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import { BuildStatus, GroupedTestStatus } from '@/components/Status/Status';

import {
  possibleBuildsTableFilter,
  possibleTestsTableFilter,
  zPossibleValidator,
} from '@/types/tree/TreeDetails';

import { TreeTableBody, zOrigin } from '@/types/tree/Tree';

import { TableRow, TableCell, TableBody } from '@/components/ui/table';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import HeaderWithInfo from '@/pages/TreeDetails/Tabs/HeaderWithInfo';

import BaseTable from './BaseTable';
import { sanitizeTableValue } from './tableUtils';

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

const headerLabelOrElement: (JSX.Element | MessagesKey)[] = [
  'treeTable.tree',
  'treeTable.branch',
  'treeTable.commitTag',
  'global.date',
  <HeaderWithInfo
    key="buildStatus"
    labelId="treeTable.build"
    tooltipId="buildTab.statusTooltip"
  />,
  <HeaderWithInfo
    key="bootStatus"
    labelId="treeTable.bootStatus"
    tooltipId="bootsTab.statusTooltip"
  />,
  <HeaderWithInfo
    key="testStatus"
    labelId="treeTable.test"
    tooltipId="testsTab.statusTooltip"
  />,
];

const treeTableHeaders = headerLabelOrElement.map(item =>
  typeof item === 'string' ? <FormattedMessage key={item} id={item} /> : item,
);

const TreeTableRow = (row: TreeTableBody): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const navigate = useNavigate({ from: '/tree' });

  const navigateToTreeDetailPage = useCallback(
    (event: React.MouseEvent<HTMLTableCellElement>) => {
      const el = event.currentTarget;
      const target = el.getAttribute('data-target');

      const safeTarget = zPossibleValidator.parse(target);

      navigate({
        to: '/tree/$treeId',
        params: { treeId: row.id },
        search: {
          tableFilter: {
            bootsTable: possibleTestsTableFilter[0],
            buildsTable: possibleBuildsTableFilter[2],
            testsTable: possibleTestsTableFilter[0],
          },
          origin: origin,
          currentTreeDetailsTab: safeTarget,
          diffFilter: {},
          treeInfo: {
            gitUrl: row.url,
            gitBranch: row.branch,
            treeName: row.tree_name ?? undefined,
            commitName: row.commitName,
            headCommitHash: row.id,
          },
        },
      });
    },
    [
      navigate,
      row.id,
      row.url,
      row.branch,
      row.tree_name,
      row.commitName,
      origin,
    ],
  );

  return (
    <TableRow>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.builds"
      >
        <Tooltip>
          <TooltipTrigger>
            <div>{sanitizeTableValue(row.tree_name ?? '', false)}</div>
          </TooltipTrigger>
          <TooltipContent>
            <a href={row.url} target="_blank" rel="noreferrer">
              {sanitizeTableValue(row.url, false)}
            </a>
          </TooltipContent>
        </Tooltip>
      </TableCell>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.builds"
      >
        {sanitizeTableValue(row.branch, false)}
      </TableCell>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.builds"
      >
        {sanitizeTableValue(row.commitName ? row.commitName : row.commitHash)}
      </TableCell>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.builds"
      >
        <TooltipDateTime dateTime={row.date} lineBreak={true} />
      </TableCell>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.builds"
      >
        {row.buildStatus ? (
          <BuildStatus
            valid={row.buildStatus.valid}
            invalid={row.buildStatus.invalid}
            unknown={row.buildStatus.null}
          />
        ) : (
          <div>Loading...</div>
        )}
      </TableCell>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.boots"
      >
        {row.bootStatus ? (
          <GroupedTestStatus
            pass={row.bootStatus.pass}
            skip={row.bootStatus.skip}
            fail={row.bootStatus.fail}
            miss={row.bootStatus.miss}
            done={row.bootStatus.done}
            error={row.bootStatus.error}
          />
        ) : (
          <div>Loading...</div>
        )}
      </TableCell>
      <TableCell
        onClick={navigateToTreeDetailPage}
        data-target="treeDetails.tests"
      >
        {row.testStatus ? (
          <GroupedTestStatus
            pass={row.testStatus.pass}
            skip={row.testStatus.skip}
            fail={row.testStatus.fail}
            miss={row.testStatus.miss}
            done={row.testStatus.done}
            error={row.testStatus.error}
          />
        ) : (
          <div>Loading...</div>
        )}
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
        tree_name={row.tree_name}
        id={row.id}
        branch={row.branch}
        date={row.date}
        url={row.url}
        commitName={row.commitName}
        bootStatus={row.bootStatus}
      />
    ));
  }, [treeTableRows]);

  return (
    <BaseTable
      headers={treeTableHeaders}
      body={<TableBody>{treeTableBody}</TableBody>}
    />
  );
};

export default TreeTable;
