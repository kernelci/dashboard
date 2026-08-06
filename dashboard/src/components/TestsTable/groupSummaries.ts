import type { GroupFieldSummary, UnifiedTestRow } from './types';

const AGGREGATED_FIELDS = [
  'start_time',
  'duration',
  'lab',
  'hardware',
  'treeBranch',
] as const;

export type AggregatedField = (typeof AGGREGATED_FIELDS)[number];

function canonicalize(value: unknown): string {
  if (value === undefined || value === null || value === '') {
    return '';
  }
  if (Array.isArray(value)) {
    return JSON.stringify(value);
  }
  return String(value);
}

function collectLeaves(rows: UnifiedTestRow[]): UnifiedTestRow[] {
  const leaves: UnifiedTestRow[] = [];
  for (const row of rows) {
    if (row.kind === 'leaf') {
      leaves.push(row);
    } else if (row.subRows) {
      leaves.push(...collectLeaves(row.subRows));
    }
  }
  return leaves;
}

function summarizeGeneric(values: unknown[]): GroupFieldSummary {
  const distinct = new Map<string, unknown>();
  for (const value of values) {
    const key = canonicalize(value);
    if (!distinct.has(key)) {
      distinct.set(key, value);
    }
  }

  if (distinct.size <= 1) {
    return { kind: 'uniform', value: distinct.values().next().value };
  }

  return { kind: 'mixed', count: distinct.size };
}

function summarizeDates(values: unknown[]): GroupFieldSummary {
  const dated = values
    .filter(
      (value): value is string => typeof value === 'string' && value !== '',
    )
    .map(value => ({ value, time: new Date(value).getTime() }))
    .filter(entry => !Number.isNaN(entry.time));

  if (dated.length === 0) {
    return { kind: 'uniform', value: undefined };
  }

  let min = dated[0];
  let max = dated[0];
  for (const entry of dated) {
    if (entry.time < min.time) {
      min = entry;
    }
    if (entry.time > max.time) {
      max = entry;
    }
  }

  if (min.time === max.time) {
    return { kind: 'uniform', value: min.value };
  }

  return { kind: 'dateRange', min: min.value, max: max.value };
}

export function buildGroupSummaries(
  children: UnifiedTestRow[],
): Partial<Record<string, GroupFieldSummary>> {
  const leaves = collectLeaves(children);
  const summaries: Partial<Record<string, GroupFieldSummary>> = {};

  for (const field of AGGREGATED_FIELDS) {
    const values = leaves.map(leaf => leaf[field]);
    summaries[field] =
      field === 'start_time'
        ? summarizeDates(values)
        : summarizeGeneric(values);
  }

  return summaries;
}

/**
 * Sort key for start_time: leaves use their date; groups use min (asc / oldest)
 * or max (desc / newest). Mixed non-date summaries are not used here.
 */
export function getDateSortKey(
  row: UnifiedTestRow,
  newestFirst: boolean,
): string | undefined {
  if (row.kind === 'leaf') {
    return row.start_time;
  }

  const summary = row.summaries?.start_time;
  if (!summary) {
    return undefined;
  }
  if (summary.kind === 'uniform') {
    return typeof summary.value === 'string' ? summary.value : undefined;
  }
  if (summary.kind === 'dateRange') {
    return newestFirst ? summary.max : summary.min;
  }
  return undefined;
}
