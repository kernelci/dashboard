import { Fragment, useState, type JSX } from 'react';

import { Link } from '@tanstack/react-router';

import { ArrowRightIcon } from 'lucide-react';
import { useIntl } from 'react-intl';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';

import { useMetrics } from '@/api/metrics';
import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import type { MetricsResponse } from '@/types/metrics';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { cn } from '@/lib/utils';
type PeriodOption = {
  labelId:
    | 'metricsPage.period.previousWeek'
    | 'metricsPage.period.previousTwoWeeks';
  days: number;
};

const PERIOD_OPTIONS: PeriodOption[] = [
  { labelId: 'metricsPage.period.previousWeek', days: 7 },
  { labelId: 'metricsPage.period.previousTwoWeeks', days: 14 },
];

type CoverageMetric = {
  label: string;
  current: number;
  previous: number;
};

type IssueDetail = {
  id: string;
  version: number;
  comment: string;
  count: number;
};

type BuildIncident = {
  origin: string;
  existingIssues: number;
  newIssues: number;
  totalIncidents: number;
  topIssues: IssueDetail[];
  newIssueDetails: IssueDetail[];
};

type LabData = {
  name: string;
  builds: number;
  boots: number;
  tests: number;
  prevTests: number;
  isNew: boolean;
  isExtinct: boolean;
};

function formatNumber(n: number): string {
  return n.toLocaleString();
}

const PERCENTAGE_BASE = 100;
const DEFAULT_INTERVAL_DAYS = 7;
const DAYS_IN_WEEK = 7;

const getCoverageMetrics = (data: MetricsResponse): CoverageMetric[] => {
  return [
    { label: 'Trees', current: data.n_trees, previous: data.prev_n_trees },
    {
      label: 'Checkouts',
      current: data.n_checkouts,
      previous: data.prev_n_checkouts,
    },
    { label: 'Builds', current: data.n_builds, previous: data.prev_n_builds },
    { label: 'Tests', current: data.n_tests, previous: data.prev_n_tests },
  ];
};

const getBuildIncidents = (data: MetricsResponse): BuildIncident[] => {
  return Object.entries(data.build_incidents_by_origin).map(
    ([origin, incidents]) => ({
      origin,
      existingIssues: incidents.n_existing_issues,
      newIssues: incidents.n_new_issues,
      totalIncidents: incidents.total_incidents,
      topIssues: (data.top_issues_by_origin[origin] ?? []).map(issue => ({
        id: issue.id,
        version: issue.version,
        comment: issue.comment,
        count: issue.total_incidents,
      })),
      newIssueDetails: (data.new_issues_by_origin[origin] ?? []).map(issue => ({
        id: issue.id,
        version: issue.version,
        comment: issue.comment,
        count: issue.total_incidents,
      })),
    }),
  );
};

function IssueDetailRow({ issue }: { issue: IssueDetail }): JSX.Element {
  return (
    <div className="flex items-start justify-between gap-3 rounded-md px-3 py-2">
      <div className="flex w-4/5 min-w-0 items-center">
        <span className="min-w-0 truncate text-sm text-gray-900">
          {issue.comment}
        </span>
        <span className="ml-2 shrink-0 text-xs text-gray-500">
          {formatNumber(issue.count)} incidents
        </span>
      </div>
      <Link
        to="/issue/$issueId"
        params={{ issueId: issue.id }}
        search={s => ({
          origin: s.origin,
          issueVersion: issue.version,
        })}
        className="flex shrink-0 items-center gap-1 text-sm text-blue-600"
      >
        View
        <ArrowRightIcon size={14} />
      </Link>
    </div>
  );
}

const getLabActivity = (data: MetricsResponse): LabData[] => {
  const allLabNames = new Set([
    ...Object.keys(data.lab_maps),
    ...Object.keys(data.prev_lab_maps),
  ]);

  return [...allLabNames]
    .map(name => {
      const current = data.lab_maps[name];
      const previous = data.prev_lab_maps[name];

      return {
        name,
        builds: current?.builds ?? 0,
        boots: current?.boots ?? 0,
        tests: current?.tests ?? 0,
        prevTests: previous?.tests ?? 0,
        isNew: current !== undefined && previous === undefined,
        isExtinct: current === undefined && previous !== undefined,
      };
    })
    .sort((left, right) => {
      if (left.isExtinct !== right.isExtinct) {
        return left.isExtinct ? 1 : -1;
      }

      return left.name.localeCompare(right.name);
    });
};

function formatDelta(current: number, previous: number): string {
  const diff = current - previous;
  if (diff === 0) {
    return 'unchanged';
  }
  const pct =
    previous !== 0 ? Math.round((diff / previous) * PERCENTAGE_BASE) : 0;
  const sign = diff > 0 ? '+' : '';
  const pctStr = previous !== 0 ? ` (${sign}${pct}%)` : '';
  return `${sign}${formatNumber(diff)}${pctStr}`;
}

function deltaColor(
  current: number,
  previous: number,
  moreIsGood = true,
): string {
  const diff = current - previous;
  if (diff === 0) {
    return 'text-gray-500';
  }
  if (moreIsGood) {
    return diff > 0 ? 'text-green-700' : 'text-red-700';
  }
  return diff > 0 ? 'text-red-700' : 'text-green-700';
}

function PeriodSelector({
  activeDays,
  onChange,
}: {
  activeDays: number;
  onChange: (days: number) => void;
}): JSX.Element {
  const { formatMessage } = useIntl();

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-gray-600">
        {formatMessage({ id: 'metricsPage.periodLabel' })}
      </span>
      {PERIOD_OPTIONS.map(opt => (
        <button
          key={opt.days}
          onClick={() => onChange(opt.days)}
          className={cn(
            'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
            opt.days === activeDays
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          )}
        >
          {formatMessage({ id: opt.labelId })}
        </button>
      ))}
    </div>
  );
}

function CoverageSection({
  metrics,
}: {
  metrics: CoverageMetric[];
}): JSX.Element {
  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Coverage</h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {metrics.map(metric => (
          <div
            key={metric.label}
            className="rounded-lg border border-gray-200 bg-white p-4"
          >
            <div className="text-sm font-medium text-gray-500">
              {metric.label}
            </div>
            <div className="mt-1 text-2xl font-bold text-gray-900">
              {formatNumber(metric.current)}
            </div>
            <div
              className={cn(
                'mt-1 text-sm',
                deltaColor(metric.current, metric.previous),
              )}
            >
              {formatDelta(metric.current, metric.previous)}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function RegressionsSection({
  regressions,
}: {
  regressions: BuildIncident[];
}): JSX.Element {
  const [expandedOrigins, setExpandedOrigins] = useState<Set<string>>(
    () => new Set(),
  );

  const toggleOrigin = (origin: string): void => {
    setExpandedOrigins(previous => {
      const next = new Set(previous);
      if (next.has(origin)) {
        next.delete(origin);
      } else {
        next.add(origin);
      }
      return next;
    });
  };

  const totalIncidents = regressions.reduce(
    (sum, r) => sum + r.totalIncidents,
    0,
  );
  const totalExisting = regressions.reduce(
    (sum, r) => sum + r.existingIssues,
    0,
  );
  const totalNew = regressions.reduce((sum, r) => sum + r.newIssues, 0);

  return (
    <section>
      <h2 className="mb-1 text-lg font-semibold text-gray-900">
        Build Regressions
      </h2>
      <p className="mb-4 text-sm text-gray-500">
        A regression is a reported problem affecting one or more builds. New
        issues are those whose first build incident occurred in this period.
      </p>
      {regressions.length === 0 ? (
        <p className="text-sm text-gray-500">
          No build regressions in this period.
        </p>
      ) : (
        <div className="rounded-lg border border-gray-200 bg-white">
          <Table className="table-fixed">
            <TableHeader>
              <TableRow>
                <TableHead className="font-bold text-black">Origin</TableHead>
                <TableHead className="font-bold text-black">
                  Issues (known + new)
                </TableHead>
                <TableHead className="font-bold text-black">
                  Affected Builds
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {regressions.map(row => {
                const isExpandable = row.newIssues > 0;
                const isExpanded = expandedOrigins.has(row.origin);

                return (
                  <Fragment key={row.origin}>
                    <TableRow>
                      <TableCell className="font-medium">
                        {isExpandable ? (
                          <button
                            type="button"
                            onClick={() => toggleOrigin(row.origin)}
                            className="flex items-center gap-2 text-left"
                            aria-expanded={isExpanded}
                          >
                            <ChevronRightAnimate isExpanded={isExpanded} />
                            {row.origin}
                          </button>
                        ) : (
                          row.origin
                        )}
                      </TableCell>
                      <TableCell>
                        {row.existingIssues} + {row.newIssues} ={' '}
                        {row.existingIssues + row.newIssues}
                        {row.newIssues > 0 && (
                          <span className="ml-2 rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700">
                            {row.newIssues} new
                          </span>
                        )}
                      </TableCell>
                      <TableCell>{formatNumber(row.totalIncidents)}</TableCell>
                    </TableRow>
                    {isExpandable && isExpanded && (
                      <TableRow key={`${row.origin}-details`}>
                        <TableCell colSpan={3} className="bg-gray-50 py-3">
                          {row.newIssueDetails.length > 0 ? (
                            <div className="space-y-1">
                              <p className="px-3 text-xs font-semibold tracking-wide text-gray-500 uppercase">
                                New regressions
                              </p>
                              {row.newIssueDetails.map(issue => (
                                <IssueDetailRow key={issue.id} issue={issue} />
                              ))}
                            </div>
                          ) : (
                            <p className="px-3 text-sm text-gray-500">
                              New issue details unavailable.
                            </p>
                          )}
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                );
              })}
              <TableRow className="bg-gray-50 font-medium">
                <TableCell className="font-bold">Total</TableCell>
                <TableCell>
                  {totalExisting} + {totalNew} = {totalExisting + totalNew}
                </TableCell>
                <TableCell>{formatNumber(totalIncidents)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      )}
    </section>
  );
}

function TopRegressionsSection({
  regressions,
}: {
  regressions: BuildIncident[];
}): JSX.Element {
  const hasIssues = regressions.some(r => r.topIssues.length > 0);

  if (!hasIssues) {
    return (
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Top Regressions
        </h2>
        <p className="text-sm text-gray-500">
          No regression details in this period.
        </p>
      </section>
    );
  }

  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Top Regressions
      </h2>
      <div className="space-y-4">
        {regressions.map(row => (
          <div
            key={row.origin}
            className="rounded-lg border border-gray-200 bg-white p-4"
          >
            <h3 className="mb-3 text-sm font-bold text-gray-700 uppercase">
              {row.origin}
            </h3>
            <div className="space-y-2">
              {row.topIssues.map((issue, idx) => (
                <div
                  key={issue.id}
                  className="flex items-start gap-3 rounded-md px-3 py-2"
                >
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600">
                    {idx + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <span className="text-sm text-gray-900">
                      {issue.comment}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      {formatNumber(issue.count)} incidents
                    </span>
                  </div>
                  <Link
                    to="/issue/$issueId"
                    params={{ issueId: issue.id }}
                    search={s => ({
                      origin: s.origin,
                      issueVersion: issue.version,
                    })}
                    className="flex shrink-0 items-center gap-1 text-sm text-blue-600"
                  >
                    View
                    <ArrowRightIcon size={14} />
                  </Link>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function LabsSection({ labs }: { labs: LabData[] }): JSX.Element {
  const activeLabs = labs.filter(l => !l.isExtinct);
  const extinctLabs = labs.filter(l => l.isExtinct);
  const totalTests = activeLabs.reduce((sum, l) => sum + l.tests, 0);
  const totalPrevTests = activeLabs.reduce((sum, l) => sum + l.prevTests, 0);
  const totalBoots = activeLabs.reduce((sum, l) => sum + l.boots, 0);

  return (
    <section>
      <div className="mb-4 flex items-baseline gap-3">
        <h2 className="text-lg font-semibold text-gray-900">
          Test Labs Activity
        </h2>
        <span className="text-sm text-gray-500">
          {activeLabs.length} lab{activeLabs.length !== 1 ? 's' : ''} reported
          results
        </span>
      </div>
      <div className="rounded-lg border border-gray-200 bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="font-bold text-black">Lab</TableHead>
              <TableHead className="font-bold text-black">Builds</TableHead>
              <TableHead className="font-bold text-black">Boots</TableHead>
              <TableHead className="font-bold text-black">Tests</TableHead>
              <TableHead className="font-bold text-black">
                Change (tests)
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {activeLabs.map(lab => (
              <TableRow key={lab.name}>
                <TableCell className="font-medium">{lab.name}</TableCell>
                <TableCell>{formatNumber(lab.builds)}</TableCell>
                <TableCell>{formatNumber(lab.boots)}</TableCell>
                <TableCell>{formatNumber(lab.tests)}</TableCell>
                <TableCell
                  className={cn(
                    'text-sm',
                    deltaColor(lab.tests, lab.prevTests),
                  )}
                >
                  {formatDelta(lab.tests, lab.prevTests)}
                </TableCell>
              </TableRow>
            ))}
            {extinctLabs.map(lab => (
              <TableRow key={lab.name} className="opacity-50">
                <TableCell className="font-medium text-gray-400">
                  {lab.name}
                  <span className="ml-2 text-xs text-gray-400">(inactive)</span>
                </TableCell>
                <TableCell className="text-gray-400">0</TableCell>
                <TableCell className="text-gray-400">0</TableCell>
                <TableCell className="text-gray-400">0</TableCell>
                <TableCell className="text-sm text-red-700">
                  {formatDelta(0, lab.prevTests)}
                </TableCell>
              </TableRow>
            ))}
            <TableRow className="bg-gray-50 font-medium">
              <TableCell className="font-bold">Total</TableCell>
              <TableCell>
                {formatNumber(activeLabs.reduce((sum, l) => sum + l.builds, 0))}
              </TableCell>
              <TableCell>{formatNumber(totalBoots)}</TableCell>
              <TableCell>{formatNumber(totalTests)}</TableCell>
              <TableCell
                className={cn(
                  'text-sm font-medium',
                  deltaColor(totalTests, totalPrevTests),
                )}
              >
                {formatDelta(totalTests, totalPrevTests)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </section>
  );
}

const getMetricsQueryParams = (
  activeDays: number,
): { startDaysAgo: number; endDaysAgo: number } => {
  const endDaysAgo = (new Date().getUTCDay() + 1) % DAYS_IN_WEEK;
  return { startDaysAgo: endDaysAgo + activeDays, endDaysAgo };
};

export const MetricsPage = (): JSX.Element => {
  const [activeDays, setActiveDays] = useState(DEFAULT_INTERVAL_DAYS);

  const { startDaysAgo, endDaysAgo } = getMetricsQueryParams(activeDays);

  const { status, data, error } = useMetrics({ startDaysAgo, endDaysAgo });

  const coverageMetrics = data ? getCoverageMetrics(data) : [];
  const regressions = data ? getBuildIncidents(data) : [];
  const labs = data ? getLabActivity(data) : [];

  return (
    <div className="flex flex-col gap-8 pb-8">
      <div className="flex justify-end">
        <PeriodSelector activeDays={activeDays} onChange={setActiveDays} />
      </div>

      <QuerySwitcher status={status} data={data} error={error}>
        <CoverageSection metrics={coverageMetrics} />
        <RegressionsSection regressions={regressions} />
        <TopRegressionsSection regressions={regressions} />
        <LabsSection labs={labs} />
      </QuerySwitcher>
    </div>
  );
};
