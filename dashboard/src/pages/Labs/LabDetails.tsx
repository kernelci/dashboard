import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type JSX,
  type ReactNode,
} from 'react';

import { format, subDays } from 'date-fns';
import { FormattedMessage, useIntl } from 'react-intl';

import {
  Link,
  useNavigate,
  useParams,
  useSearch,
  type LinkProps,
} from '@tanstack/react-router';

import { BaseCard } from '@/components/Cards/BaseCard';
import { LineChart } from '@/components/LineChart';
import { Colors } from '@/components/StatusChart/StatusCharts';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/Breadcrumb/Breadcrumb';
import MemoizedIssuesList from '@/components/Cards/IssuesList';
import { IndeterminateCheckbox } from '@/components/Checkbox/IndeterminateCheckbox';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import PageWithTitle from '@/components/PageWithTitle';
import { GroupedTestStatus } from '@/components/Status/Status';
import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { MemoizedStatusCard } from '@/components/Tabs/StatusCard';
import Tabs from '@/components/Tabs/Tabs';
import { TestsTable } from '@/components/TestsTable/TestsTable';
import { CommitTagTooltip } from '@/components/Tooltip/CommitTagTooltip';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import type { MessagesKey } from '@/locales/messages';
import { DEFAULT_DIFF_FILTER, type RequiredStatusCount } from '@/types/general';
import { zPossibleTabValidator } from '@/types/tree/TreeDetails';
import {
  defaultTableStatusSelection,
  toggleTableStatus,
  type TableStatusOption,
  type TableStatusSelection,
} from '@/utils/tableStatusFilter';

import LabProvided from './LabProvided';
import {
  aggregateLabTrees,
  dailyStatus,
  labDetailsMock,
  sumStatusCounts,
  toTestHistory,
  type LabDailyKind,
  type LabTestRow,
  type LabTreeMock,
} from './labDetailsMock';

const dayLabels = (days: number): string[] =>
  Array.from({ length: days }, (_, index) =>
    format(subDays(new Date(), days - 1 - index), 'MMM d'),
  );

const LabDailyGraph = ({
  treeCount,
  days,
  kind,
  titleId,
}: {
  treeCount: number;
  days: number;
  kind: LabDailyKind;
  titleId: MessagesKey;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const counts = dailyStatus(kind, days, treeCount);

  return (
    <BaseCard
      title={formatMessage({ id: titleId })}
      content={
        <LineChart
          height={400}
          margin={{ top: 80 }}
          xAxis={[
            {
              scaleType: 'point',
              data: dayLabels(days),
              tickLabelInterval: 'auto',
            },
          ]}
          series={[
            {
              id: 'good',
              label: formatMessage({ id: 'global.success' }),
              data: counts.pass,
              color: Colors.Green,
            },
            {
              id: 'bad',
              label: formatMessage({ id: 'global.failed' }),
              data: counts.fail,
              color: Colors.Red,
            },
            {
              id: 'mid',
              label: formatMessage({ id: 'global.inconclusive' }),
              data: counts.inconclusive,
              color: Colors.Gray,
            },
          ]}
          slotProps={{
            legend: {
              position: { vertical: 'top', horizontal: 'middle' },
            },
          }}
        />
      }
    />
  );
};

const LabTestsTable = ({
  rows,
  labName,
}: {
  rows: LabTestRow[];
  labName: string;
}): JSX.Element => {
  const [filter, setFilter] = useState<TableStatusSelection>(() => [
    ...defaultTableStatusSelection,
  ]);
  const [pathFilter, setPathFilter] = useState('');
  const testHistory = useMemo(
    () => toTestHistory(rows, labName),
    [labName, rows],
  );
  const onToggleFilter = useCallback((option: TableStatusOption) => {
    setFilter(current => toggleTableStatus(current, option));
  }, []);
  const getRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/test/$testId',
      params: { testId },
      search: previous => ({ origin: previous.origin }),
    }),
    [],
  );

  return (
    <TestsTable
      tableKey="treeDetailsTests"
      testHistory={testHistory}
      filter={filter}
      onToggleFilter={onToggleFilter}
      getRowLink={getRowLink}
      updatePathFilter={setPathFilter}
      currentPathFilter={pathFilter}
    />
  );
};

const statusCounts = (summary: RequiredStatusCount): JSX.Element => (
  <GroupedTestStatus
    pass={summary.PASS}
    fail={summary.FAIL}
    error={summary.ERROR}
    miss={summary.MISS}
    skip={summary.SKIP}
    done={summary.DONE}
    nullStatus={summary.NULL}
    hideInconclusive
  />
);

const MockTable = ({
  headers,
  rows,
}: {
  headers: MessagesKey[];
  rows: { key: string; cells: ReactNode[] }[];
}): JSX.Element => (
  <BaseTable
    headerComponents={headers.map(id => (
      <TableHead key={id}>
        <FormattedMessage id={id} />
      </TableHead>
    ))}
  >
    <TableBody>
      {rows.map(row => (
        <TableRow key={row.key}>
          {row.cells.map((cell, index) => (
            <TableCell key={headers[index]}>{cell}</TableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  </BaseTable>
);

const LabDetails = (): JSX.Element => {
  const { labName } = useParams({ from: '/_main/labs/$labName' });
  const { origin, intervalInDays, currentPageTab, labDetailsPreview } =
    useSearch({ from: '/_main/labs/$labName' });
  const navigate = useNavigate({ from: '/labs/$labName' });
  const { formatMessage } = useIntl();
  const trees = useMemo(() => labDetailsMock(labName), [labName]);
  const [selectedKeys, setSelectedKeys] = useState<string[] | null>(null);
  const showEmpty = labDetailsPreview === 'empty';
  const selection = selectedKeys ?? trees.map(tree => tree.key);
  const selectedTrees = trees.filter(tree => selection.includes(tree.key));
  const summary = aggregateLabTrees(selectedTrees);
  const allSelected = selection.length === trees.length;
  const noopFilter = useCallback(() => undefined, []);

  useEffect(() => {
    setSelectedKeys(null);
  }, [labName]);

  const onTabChange = useCallback(
    (value: string) => {
      navigate({
        search: previous => ({
          ...previous,
          currentPageTab: zPossibleTabValidator.parse(value),
        }),
        state: s => s,
      });
    },
    [navigate],
  );

  const toggleTree = (key: string): void => {
    const next = new Set(selection);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    setSelectedKeys([...next]);
  };

  return (
    <PageWithTitle
      title={formatMessage({ id: 'labDetails.title' }, { lab: labName })}
    >
      <div className="flex flex-col gap-6 pb-10" data-test-id="lab-details">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink
                  to="/labs"
                  search={previous => ({
                    origin: previous.origin,
                    intervalInDays: previous.intervalInDays,
                    labsSearch: previous.labsSearch,
                    listingSize: previous.listingSize,
                  })}
                  state={s => s}
                >
                  <FormattedMessage id="global.labs" />
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>{labName}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <p className="text-sm font-medium text-gray-900">
            <FormattedMessage
              id="labDetails.window"
              values={{ origin, days: intervalInDays }}
            />
          </p>
        </div>

        {showEmpty ? (
          <div data-test-id="lab-details-empty">
            <MemoizedSectionError
              isLoading={false}
              isEmpty
              variant="warning"
              emptyLabel="global.noResults"
            />
            <div className="flex justify-center pb-6">
              <Button variant="outline" asChild>
                <Link
                  to="/labs"
                  search={previous => ({
                    origin: previous.origin,
                    intervalInDays: previous.intervalInDays,
                    labsSearch: previous.labsSearch,
                    listingSize: previous.listingSize,
                  })}
                  state={s => s}
                >
                  <FormattedMessage id="labDetails.back" />
                </Link>
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-5 flex flex-col">
            <LabProvided
              builds={trees.flatMap(tree => tree.buildRows)}
              boots={trees.flatMap(tree => tree.bootRows)}
              tests={trees.flatMap(tree => tree.testRows)}
              buildCounts={sumStatusCounts(trees.map(tree => tree.builds))}
              bootCounts={sumStatusCounts(trees.map(tree => tree.boots))}
              testCounts={sumStatusCounts(trees.map(tree => tree.tests))}
              checkoutTotal={trees.length}
              checkoutsBuilt={
                trees.filter(tree => tree.buildRows.length > 0).length
              }
              checkoutsBooted={
                trees.filter(tree => tree.bootRows.length > 0).length
              }
              checkoutsTested={
                trees.filter(tree => tree.testRows.length > 0).length
              }
            />
            <Separator className="bg-dark-gray my-6" />
            <TreeTable
              trees={trees}
              selection={selection}
              allSelected={allSelected}
              onToggleAll={() =>
                setSelectedKeys(allSelected ? [] : trees.map(tree => tree.key))
              }
              onToggleTree={toggleTree}
            />
            {selectedTrees.length === 0 ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-center">
                  <h3 className="text-lg font-medium">
                    <FormattedMessage id="hardwareDetails.selectTreeTitle" />
                  </h3>
                  <p className="m-4 mx-auto max-w-lg">
                    <FormattedMessage id="labDetails.selectTreeMessage" />
                  </p>
                </div>
              </div>
            ) : (
              <Tabs
                tabs={[
                  {
                    name: 'global.builds',
                    rightElement: statusCounts(summary.builds),
                    content: (
                      <div className="flex flex-col gap-8 pt-4 pb-10">
                        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                          <div>
                            <MemoizedStatusCard
                              title={
                                <FormattedMessage id="buildTab.buildStatus" />
                              }
                              statusCounts={summary.builds}
                              filterStatusKey="buildStatus"
                              toggleFilterBySection={noopFilter}
                            />
                            <MemoizedIssuesList
                              title={<FormattedMessage id="global.issues" />}
                              issues={summary.buildIssues}
                              diffFilter={DEFAULT_DIFF_FILTER}
                              issueFilterSection="buildIssue"
                            />
                          </div>
                          <LabDailyGraph
                            treeCount={selectedTrees.length}
                            days={intervalInDays}
                            kind="builds"
                            titleId="labDetails.buildsPerDay"
                          />
                        </div>
                        <ResultTable
                          titleId="global.builds"
                          headers={[
                            'global.treeBranch',
                            'global.config',
                            'global.architecture',
                            'global.compiler',
                            'global.status',
                            'labDetails.started',
                          ]}
                          rows={summary.buildRows.map(row => ({
                            key: `${row.tree}-${row.config}-${row.arch}-${row.started}`,
                            cells: [
                              `${row.tree} / ${row.branch}`,
                              row.config,
                              row.arch,
                              row.compiler,
                              row.status,
                              row.started,
                            ],
                          }))}
                        />
                      </div>
                    ),
                  },
                  {
                    name: 'global.boots',
                    rightElement: statusCounts(summary.boots),
                    content: (
                      <BootOrTestTab
                        kind="boots"
                        statusTitleId="bootsTab.bootStatus"
                        statusCountsValue={summary.boots}
                        issues={summary.bootIssues}
                        issueFilterSection="bootIssue"
                        rows={summary.bootRows.map(row => ({
                          key: `${row.tree}-${row.platform}-${row.started}`,
                          cells: [
                            `${row.tree} / ${row.branch}`,
                            row.platform,
                            row.status,
                            row.started,
                          ],
                        }))}
                        rowHeaders={[
                          'global.treeBranch',
                          'global.platform',
                          'global.status',
                          'labDetails.started',
                        ]}
                        titleId="global.boots"
                        noopFilter={noopFilter}
                        treeCount={selectedTrees.length}
                        intervalInDays={intervalInDays}
                      />
                    ),
                  },
                  {
                    name: 'global.tests',
                    rightElement: statusCounts(summary.tests),
                    content: (
                      <BootOrTestTab
                        kind="tests"
                        statusTitleId="testsTab.testStatus"
                        statusCountsValue={summary.tests}
                        issues={summary.testIssues}
                        issueFilterSection="testIssue"
                        results={
                          <LabTestsTable
                            rows={summary.testRows}
                            labName={labName}
                          />
                        }
                        noopFilter={noopFilter}
                        treeCount={selectedTrees.length}
                        intervalInDays={intervalInDays}
                      />
                    ),
                  },
                ]}
                value={currentPageTab}
                onValueChange={onTabChange}
              />
            )}
          </div>
        )}
      </div>
    </PageWithTitle>
  );
};

const TreeTable = ({
  trees,
  selection,
  allSelected,
  onToggleAll,
  onToggleTree,
}: {
  trees: LabTreeMock[];
  selection: string[];
  allSelected: boolean;
  onToggleAll: () => void;
  onToggleTree: (key: string) => void;
}): JSX.Element => (
  <BaseTable
    headerComponents={[
      <TableHead key="select">
        <IndeterminateCheckbox
          checked={allSelected}
          indeterminate={selection.length > 0 && !allSelected}
          onChange={onToggleAll}
        />
      </TableHead>,
      <TableHead key="tree">
        <FormattedMessage id="globalTable.tree" />
      </TableHead>,
      <TableHead key="branch">
        <FormattedMessage id="globalTable.branch" />
      </TableHead>,
      <TableHead key="commit">
        <FormattedMessage id="globalTable.commitTag" />
      </TableHead>,
      <TableHead key="build">
        <FormattedMessage id="globalTable.build" />
      </TableHead>,
      <TableHead key="boot">
        <FormattedMessage id="globalTable.bootStatus" />
      </TableHead>,
      <TableHead key="test">
        <FormattedMessage id="globalTable.test" />
      </TableHead>,
    ]}
  >
    <TableBody>
      {trees.map(tree => (
        <TableRow key={tree.key}>
          <TableCell>
            <IndeterminateCheckbox
              checked={selection.includes(tree.key)}
              onChange={() => onToggleTree(tree.key)}
            />
          </TableCell>
          <TableCell>{tree.tree}</TableCell>
          <TableCell>{tree.branch}</TableCell>
          <TableCell>
            <CommitTagTooltip
              commitName={tree.commitName}
              commitHash={tree.commitHash}
              commitTags={[tree.commitName]}
            />
          </TableCell>
          <TableCell>{statusCounts(tree.builds)}</TableCell>
          <TableCell>{statusCounts(tree.boots)}</TableCell>
          <TableCell>{statusCounts(tree.tests)}</TableCell>
        </TableRow>
      ))}
    </TableBody>
  </BaseTable>
);

const ResultTable = ({
  titleId,
  headers,
  rows,
}: {
  titleId: MessagesKey;
  headers: MessagesKey[];
  rows: { key: string; cells: ReactNode[] }[];
}): JSX.Element => (
  <div className="flex flex-col gap-4">
    <div className="text-lg">
      <FormattedMessage id={titleId} />
    </div>
    <MockTable headers={headers} rows={rows} />
  </div>
);

const BootOrTestTab = ({
  kind,
  statusTitleId,
  statusCountsValue,
  issues,
  issueFilterSection,
  rows,
  rowHeaders,
  titleId,
  results,
  noopFilter,
  treeCount,
  intervalInDays,
}: {
  kind: 'boots' | 'tests';
  statusTitleId: MessagesKey;
  statusCountsValue: RequiredStatusCount;
  issues: LabTreeMock['bootIssues'];
  issueFilterSection: 'bootIssue' | 'testIssue';
  rows?: { key: string; cells: ReactNode[] }[];
  rowHeaders?: MessagesKey[];
  titleId?: MessagesKey;
  results?: ReactNode;
  noopFilter: () => undefined;
  treeCount: number;
  intervalInDays: number;
}): JSX.Element => (
  <div className="flex flex-col gap-8 pt-4 pb-10">
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div>
        <MemoizedStatusCard
          title={<FormattedMessage id={statusTitleId} />}
          statusCounts={statusCountsValue}
          filterStatusKey={kind === 'boots' ? 'bootStatus' : 'testStatus'}
          toggleFilterBySection={noopFilter}
        />
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={issues}
          diffFilter={DEFAULT_DIFF_FILTER}
          issueFilterSection={issueFilterSection}
        />
      </div>
      <LabDailyGraph
        treeCount={treeCount}
        days={intervalInDays}
        kind={kind}
        titleId={
          kind === 'boots' ? 'labDetails.bootsPerDay' : 'labDetails.testsPerDay'
        }
      />
    </div>
    {results ??
      (titleId && rowHeaders && rows ? (
        <ResultTable titleId={titleId} headers={rowHeaders} rows={rows} />
      ) : null)}
  </div>
);

export default LabDetails;
