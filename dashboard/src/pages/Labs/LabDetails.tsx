import {
  useCallback,
  useEffect,
  useState,
  type JSX,
  type ReactNode,
} from 'react';

import { format } from 'date-fns';
import { MdWarningAmber } from 'react-icons/md';
import { FormattedMessage, useIntl } from 'react-intl';

import {
  Link,
  useNavigate,
  useParams,
  useSearch,
  type LinkProps,
} from '@tanstack/react-router';

import {
  useLabAttention,
  useLabBoots,
  useLabBuilds,
  useLabDetails,
  useLabTests,
} from '@/api/labDetails';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';
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
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Separator } from '@/components/ui/separator';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import type { Status } from '@/types/database';
import type { MessagesKey } from '@/locales/messages';
import type {
  LabAttentionItem,
  LabDailyPoint,
  LabDetailsTree,
  LabTestRow,
} from '@/types/labDetails';
import {
  DEFAULT_DIFF_FILTER,
  type RequiredStatusCount,
  type TestHistory,
} from '@/types/general';
import type { TIssue } from '@/types/issues';
import { zPossibleTabValidator } from '@/types/tree/TreeDetails';
import {
  defaultTableStatusSelection,
  toggleTableStatus,
  type TableStatusOption,
  type TableStatusSelection,
} from '@/utils/tableStatusFilter';
import { status } from '@/utils/constants/database';
import { formatDate } from '@/utils/utils';

import LabProvided from './LabProvided';
import {
  attentionLines,
  checkedTreeParams,
  sumLabTrees,
  toStatusCount,
} from './labDetails';

const dayLabel = (day: string): string => {
  const [year, month, date] = day.split('-').map(Number);
  if (!year || !month || !date) {
    return day;
  }
  return format(new Date(year, month - 1, date), 'MMM d');
};

const startedLabel = (value: string | null | undefined): string =>
  value ? formatDate(value, true) : '-';

const commitTags = (name: string | null | undefined): string[] | undefined =>
  name ? [name] : undefined;

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

const LabDailyGraph = ({
  points,
  titleId,
}: {
  points: LabDailyPoint[];
  titleId: MessagesKey;
}): JSX.Element => {
  const { formatMessage } = useIntl();

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
              data: points.map(point => dayLabel(point.day)),
              tickLabelInterval: 'auto',
            },
          ]}
          series={[
            {
              id: 'good',
              label: formatMessage({ id: 'global.success' }),
              data: points.map(point => point.pass_count),
              color: Colors.Green,
            },
            {
              id: 'bad',
              label: formatMessage({ id: 'global.failed' }),
              data: points.map(point => point.fail_count),
              color: Colors.Red,
            },
            {
              id: 'mid',
              label: formatMessage({ id: 'global.inconclusive' }),
              data: points.map(point => point.inconclusive_count),
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
  </div>
);

const TableSlot = ({
  isLoading,
  errorMessage,
  children,
}: {
  isLoading: boolean;
  errorMessage?: string;
  children: ReactNode;
}): JSX.Element => {
  if (isLoading) {
    return <MemoizedSectionError isLoading />;
  }
  if (errorMessage) {
    return <MemoizedSectionError errorMessage={errorMessage} />;
  }
  return <>{children}</>;
};

const isStatus = (value: string): value is Status =>
  (status as readonly string[]).includes(value);

const toTestHistory = (row: LabTestRow): TestHistory => {
  const fromMisc = row.environment_misc?.platform;
  const platform =
    row.platform ?? (typeof fromMisc === 'string' ? fromMisc : undefined);
  return {
    id: row.id,
    status: isStatus(row.status) ? row.status : 'NULL',
    path: row.path ?? undefined,
    start_time: row.start_time ?? undefined,
    duration: row.duration ?? undefined,
    tree_name: row.tree_name,
    git_repository_branch: row.git_repository_branch,
    lab: row.lab,
    config: row.config_name ?? undefined,
    arch: row.architecture ?? undefined,
    platform,
    environment_misc: platform ? { platform } : undefined,
  };
};

const LabTestsTable = ({ rows }: { rows: LabTestRow[] }): JSX.Element => {
  const [filter, setFilter] = useState<TableStatusSelection>(() => [
    ...defaultTableStatusSelection,
  ]);
  const [pathFilter, setPathFilter] = useState('');
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
      testHistory={rows.map(toTestHistory)}
      filter={filter}
      onToggleFilter={onToggleFilter}
      getRowLink={getRowLink}
      updatePathFilter={setPathFilter}
      currentPathFilter={pathFilter}
    />
  );
};

const TreeTable = ({
  trees,
  selection,
  allSelected,
  onToggleAll,
  onToggleTree,
}: {
  trees: LabDetailsTree[];
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
          <TableCell>{tree.tree_name}</TableCell>
          <TableCell>{tree.git_branch}</TableCell>
          <TableCell>
            <CommitTagTooltip
              commitName={tree.commit_name ?? undefined}
              commitHash={tree.commit_hash ?? undefined}
              commitTags={commitTags(tree.commit_name)}
            />
          </TableCell>
          <TableCell>{statusCounts(toStatusCount(tree.builds))}</TableCell>
          <TableCell>{statusCounts(toStatusCount(tree.boots))}</TableCell>
          <TableCell>{statusCounts(toStatusCount(tree.tests))}</TableCell>
        </TableRow>
      ))}
    </TableBody>
  </BaseTable>
);

const LabAttention = ({
  items,
}: {
  items: LabAttentionItem[];
}): JSX.Element | null => {
  const lines = attentionLines(items);
  if (!lines) {
    return null;
  }

  return (
    <Collapsible
      className="group border-dark-gray mb-6 overflow-hidden rounded-xl border bg-white text-sm text-black"
      data-test-id="lab-attention"
    >
      <CollapsibleTrigger className="flex w-full items-center gap-2 bg-amber-50 px-3 py-2 text-left text-amber-950">
        <MdWarningAmber className="size-5 shrink-0" aria-hidden />
        <span className="font-medium">
          {lines.map((test, index) => {
            const item = items[index];
            if (!item) {
              return null;
            }
            return (
              <span
                key={`${item.kind}-${item.path ?? ''}-${item.platform}-${item.tree_name}-${item.commit_hash ?? ''}`}
              >
                {index > 0 && ' / '}
                <FormattedMessage
                  id="labDetails.attentionProblem"
                  values={{ test, platform: item.platform }}
                />
              </span>
            );
          })}
        </span>
        <ChevronRightAnimate className="ml-auto size-5 shrink-0" />
      </CollapsibleTrigger>
      <CollapsibleContent>
        {items.map(item => (
          <div
            key={`${item.kind}-${item.path ?? ''}-${item.platform}-${item.tree_name}-${item.commit_hash ?? ''}`}
            className="border-dark-gray border-t px-4 py-3"
          >
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {(
                [
                  ['global.platform', item.platform],
                  [
                    'global.treeBranch',
                    `${item.tree_name} / ${item.git_branch}`,
                  ],
                  [
                    'globalTable.commitTag',
                    <CommitTagTooltip
                      key={item.commit_hash}
                      commitName={item.commit_name ?? undefined}
                      commitHash={item.commit_hash ?? undefined}
                      commitTags={commitTags(item.commit_name)}
                    />,
                  ],
                  ['global.config', item.config_name],
                  ['global.architecture', item.architecture],
                  ['global.compiler', item.compiler],
                  ['global.date', item.last_failure_date],
                ] as [MessagesKey, ReactNode][]
              ).map(([labelId, value]) => (
                <div key={labelId}>
                  <div className="text-xs text-gray-500">
                    <FormattedMessage id={labelId} />
                  </div>
                  <div className="break-all">{value}</div>
                </div>
              ))}
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-gray-500">
                <FormattedMessage id="labDetails.passedIn" />
              </span>
              {item.passed_labs.map(lab => (
                <Badge
                  key={lab}
                  variant="greenTag"
                  className="text-sm font-normal text-nowrap normal-case"
                >
                  {lab}
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  );
};

const backToLabs = (previous: {
  origin?: string;
  intervalInDays?: number;
  labsSearch?: string;
  listingSize?: number;
}): {
  origin?: string;
  intervalInDays?: number;
  labsSearch?: string;
  listingSize?: number;
} => ({
  origin: previous.origin,
  intervalInDays: previous.intervalInDays,
  labsSearch: previous.labsSearch,
  listingSize: previous.listingSize,
});

const StatusPane = ({
  titleId,
  counts,
  issues,
  filterKey,
  issueFilterSection,
  points,
  chartTitleId,
  table,
}: {
  titleId: MessagesKey;
  counts: RequiredStatusCount;
  issues: TIssue[];
  filterKey: 'buildStatus' | 'bootStatus' | 'testStatus';
  issueFilterSection: 'buildIssue' | 'bootIssue' | 'testIssue';
  points: LabDailyPoint[];
  chartTitleId: MessagesKey;
  table: ReactNode;
}): JSX.Element => (
  <div className="flex flex-col gap-8 pt-4 pb-10">
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div>
        <MemoizedStatusCard
          title={<FormattedMessage id={titleId} />}
          statusCounts={counts}
          filterStatusKey={filterKey}
          toggleFilterBySection={() => undefined}
        />
        <MemoizedIssuesList
          title={<FormattedMessage id="global.issues" />}
          issues={issues}
          diffFilter={DEFAULT_DIFF_FILTER}
          issueFilterSection={issueFilterSection}
        />
      </div>
      <LabDailyGraph points={points} titleId={chartTitleId} />
    </div>
    {table}
  </div>
);

const LabDetails = (): JSX.Element => {
  const { labName } = useParams({ from: '/_main/labs/$labName' });
  const { origin, intervalInDays, currentPageTab } = useSearch({
    from: '/_main/labs/$labName',
  });
  const navigate = useNavigate({ from: '/labs/$labName' });
  const { formatMessage } = useIntl();
  const details = useLabDetails(labName);
  const trees = details.data?.trees ?? [];
  const [selectedKeys, setSelectedKeys] = useState<string[] | null>(null);
  const selection = selectedKeys ?? trees.map(tree => tree.key);
  const selectedTrees = trees.filter(tree => selection.includes(tree.key));
  const summary = sumLabTrees(selectedTrees);
  const allSelected = trees.length > 0 && selection.length === trees.length;
  const treeFilter = checkedTreeParams(trees.length, selection);
  const rowsEnabled = trees.length > 0 && selection.length > 0;
  const builds = useLabBuilds(labName, treeFilter, rowsEnabled);
  const boots = useLabBoots(labName, treeFilter, rowsEnabled);
  const tests = useLabTests(labName, treeFilter, rowsEnabled);
  const [loadAttention, setLoadAttention] = useState(false);
  const attention = useLabAttention(labName, loadAttention);
  const treeKeyList = trees.map(tree => tree.key).join('\n');

  useEffect(() => {
    setSelectedKeys(null);
  }, [labName, treeKeyList]);

  useEffect(() => {
    setLoadAttention(trees.length > 0);
  }, [trees.length]);

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

  const showEmpty = details.isSuccess && trees.length === 0;

  return (
    <PageWithTitle
      title={formatMessage({ id: 'labDetails.title' }, { lab: labName })}
    >
      <div className="flex flex-col gap-6 pb-10" data-test-id="lab-details">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink to="/labs" search={backToLabs} state={s => s}>
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

        {details.isLoading ? (
          <MemoizedSectionError isLoading />
        ) : details.isError ? (
          <MemoizedSectionError errorMessage={details.error.message} />
        ) : showEmpty ? (
          <div data-test-id="lab-details-empty">
            <MemoizedSectionError
              isLoading={false}
              isEmpty
              variant="warning"
              emptyLabel="global.noResults"
            />
            <div className="flex justify-center pb-6">
              <Button variant="outline" asChild>
                <Link to="/labs" search={backToLabs} state={s => s}>
                  <FormattedMessage id="labDetails.back" />
                </Link>
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-5 flex flex-col">
            <LabAttention items={attention.data ?? []} />
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
                      <StatusPane
                        titleId="buildTab.buildStatus"
                        counts={summary.builds}
                        issues={summary.buildIssues}
                        filterKey="buildStatus"
                        issueFilterSection="buildIssue"
                        points={summary.daily.builds}
                        chartTitleId="labDetails.buildsPerDay"
                        table={
                          <TableSlot
                            isLoading={builds.isLoading}
                            errorMessage={
                              builds.isError ? builds.error.message : undefined
                            }
                          >
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
                              rows={(builds.data ?? []).map((row, index) => ({
                                key: `${index}-${row.tree_name}-${row.start_time ?? ''}`,
                                cells: [
                                  `${row.tree_name} / ${row.git_branch}`,
                                  row.config_name,
                                  row.architecture,
                                  row.compiler,
                                  row.status,
                                  startedLabel(row.start_time),
                                ],
                              }))}
                            />
                          </TableSlot>
                        }
                      />
                    ),
                  },
                  {
                    name: 'global.boots',
                    rightElement: statusCounts(summary.boots),
                    content: (
                      <StatusPane
                        titleId="bootsTab.bootStatus"
                        counts={summary.boots}
                        issues={summary.bootIssues}
                        filterKey="bootStatus"
                        issueFilterSection="bootIssue"
                        points={summary.daily.boots}
                        chartTitleId="labDetails.bootsPerDay"
                        table={
                          <TableSlot
                            isLoading={boots.isLoading}
                            errorMessage={
                              boots.isError ? boots.error.message : undefined
                            }
                          >
                            <ResultTable
                              titleId="global.boots"
                              headers={[
                                'global.treeBranch',
                                'global.platform',
                                'global.status',
                                'labDetails.started',
                              ]}
                              rows={(boots.data ?? []).map((row, index) => ({
                                key: `${index}-${row.tree_name}-${row.platform}-${row.start_time ?? ''}`,
                                cells: [
                                  `${row.tree_name} / ${row.git_branch}`,
                                  row.platform,
                                  row.status,
                                  startedLabel(row.start_time),
                                ],
                              }))}
                            />
                          </TableSlot>
                        }
                      />
                    ),
                  },
                  {
                    name: 'global.tests',
                    rightElement: statusCounts(summary.tests),
                    content: (
                      <StatusPane
                        titleId="testsTab.testStatus"
                        counts={summary.tests}
                        issues={summary.testIssues}
                        filterKey="testStatus"
                        issueFilterSection="testIssue"
                        points={summary.daily.tests}
                        chartTitleId="labDetails.testsPerDay"
                        table={
                          <TableSlot
                            isLoading={tests.isLoading}
                            errorMessage={
                              tests.isError ? tests.error.message : undefined
                            }
                          >
                            <LabTestsTable rows={tests.data ?? []} />
                          </TableSlot>
                        }
                      />
                    ),
                  },
                ]}
                value={currentPageTab}
                onValueChange={onTabChange}
              />
            )}
            {details.data ? (
              <>
                <Separator className="bg-dark-gray my-6" />
                <LabProvided
                  distribution={details.data.distribution}
                  fill={details.data.fill}
                />
              </>
            ) : null}
          </div>
        )}
      </div>
    </PageWithTitle>
  );
};

export default LabDetails;
