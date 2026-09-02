import type {
  CompareBootFailureRow,
  CompareBuildFailureRow,
  CompareChangeType,
  CompareGroupedApiStatus,
  CompareItemStatus,
  CompareRowChange,
  CompareStatusPair,
  CompareTestFailureRow,
  TreeCompareBuildDiffApiRow,
  TreeCompareTestDiffApiRow,
} from '@/types/tree/TreeCompare';
import {
  compareAbsentStatusToken,
  compareChangeTypes,
  compareDefaultStatusPairParams,
  compareEmptyStatusPairsToken,
  compareItemStatuses,
  compareStatusPairStorageKey,
} from '@/types/tree/TreeCompare';

export function apiStatusToItemStatus(
  status: CompareGroupedApiStatus | null | undefined,
): CompareItemStatus {
  if (!status) {
    return '—';
  }
  return status;
}

/** Mirror backend _CHANGE_COUNT_SELECT categories for A→B transitions. */
export function deriveCompareChange(
  statusA: CompareItemStatus,
  statusB: CompareItemStatus,
): CompareRowChange {
  // Same status on both sides is no change; only FAIL→FAIL has a backend count.
  if (statusA === statusB && statusA !== 'FAIL') {
    return 'unchanged';
  }
  // Present on A, absent on B — was wrongly folded into regression/fixed.
  if (statusA !== '—' && statusB === '—') {
    return 'disappeared';
  }
  // Absent on A, present on B.
  if (statusA === '—' && statusB !== '—') {
    if (statusB === 'FAIL') {
      return 'newFailure';
    }
    if (statusB === 'PASS') {
      return 'newPass';
    }
    return 'appeared';
  }
  if (statusA === 'PASS' && statusB === 'FAIL') {
    return 'regression';
  }
  if (statusA === 'FAIL' && statusB === 'PASS') {
    return 'fixed';
  }
  if (statusA === 'FAIL' && statusB === 'FAIL') {
    return 'stillFailing';
  }
  // Both sides present; remaining transitions involve INCONCLUSIVE.
  if (statusB === 'FAIL') {
    return 'newFailure';
  }
  if (statusB === 'PASS') {
    return statusA === 'FAIL' ? 'fixed' : 'newPass';
  }
  // PASS/FAIL → INCONCLUSIVE (INCONCLUSIVE→INCONCLUSIVE should not reach here).
  if (statusA === 'PASS') {
    return 'regression';
  }
  if (statusA === 'FAIL') {
    return 'fixed';
  }
  return 'appeared';
}

/** Status pairs that currently classify as each change-type chip. */
export const changeTypeStatusPairs: Record<
  CompareChangeType,
  CompareStatusPair[]
> = Object.fromEntries(
  compareChangeTypes.map(change => [change, [] as CompareStatusPair[]]),
) as Record<CompareChangeType, CompareStatusPair[]>;

for (const from of compareItemStatuses) {
  for (const to of compareItemStatuses) {
    const change = deriveCompareChange(from, to);
    if (change !== 'unchanged') {
      changeTypeStatusPairs[change].push({ from, to });
    }
  }
}

export function changeTypeIsSelected(
  pairs: readonly CompareStatusPair[],
  change: CompareChangeType,
): boolean {
  const selected = new Set(
    normalizeStatusPairs(pairs).map(serializeStatusPair),
  );
  const required = changeTypeStatusPairs[change];
  return (
    required.length > 0 &&
    required.every(pair => selected.has(serializeStatusPair(pair)))
  );
}

/** Add every pair for a change type, or remove them all if already complete. */
export function toggleChangeTypePairs(
  current: readonly CompareStatusPair[],
  change: CompareChangeType,
): CompareStatusPair[] {
  const target = changeTypeStatusPairs[change];
  if (changeTypeIsSelected(current, change)) {
    const remove = new Set(target.map(serializeStatusPair));
    return normalizeStatusPairs(
      current.filter(pair => !remove.has(serializeStatusPair(pair))),
    );
  }
  return normalizeStatusPairs([...current, ...target]);
}

export function mapBuildDiffRows(
  rows: TreeCompareBuildDiffApiRow[],
): CompareBuildFailureRow[] {
  return rows.map(row => {
    const sideA = apiStatusToItemStatus(row.status_a);
    const sideB = apiStatusToItemStatus(row.status_b);
    return {
      id: `build:${row.config_name}:${row.architecture}:${row.compiler}`,
      config: row.config_name,
      arch: row.architecture,
      compiler: row.compiler,
      sideA,
      sideB,
      change: deriveCompareChange(sideA, sideB),
    };
  });
}

export function mapBootOrTestDiffRows(
  rows: TreeCompareTestDiffApiRow[],
  kind: 'boot' | 'test',
): Array<CompareBootFailureRow | CompareTestFailureRow> {
  return rows.map(row => {
    const sideA = apiStatusToItemStatus(row.status_a);
    const sideB = apiStatusToItemStatus(row.status_b);
    return {
      id: `${kind}:${row.path}:${row.config_name}:${row.architecture}:${row.platform}`,
      path: row.path,
      config: row.config_name,
      arch: row.architecture,
      hardware: row.platform,
      sideA,
      sideB,
      change: deriveCompareChange(sideA, sideB),
    };
  });
}

function isCompareItemStatus(value: string): value is CompareItemStatus {
  return (compareItemStatuses as readonly string[]).includes(value);
}

function encodeStatus(status: CompareItemStatus): string {
  return status === '—' ? compareAbsentStatusToken : status;
}

function decodeStatus(raw: string): CompareItemStatus | undefined {
  if (raw === compareAbsentStatusToken) {
    return '—';
  }
  return isCompareItemStatus(raw) ? raw : undefined;
}

export function serializeStatusPair(pair: CompareStatusPair): string {
  return `${encodeStatus(pair.from)}:${encodeStatus(pair.to)}`;
}

export function parseStatusPair(raw: string): CompareStatusPair | undefined {
  const separatorIndex = raw.indexOf(':');
  if (separatorIndex === -1) {
    return undefined;
  }
  const from = decodeStatus(raw.slice(0, separatorIndex));
  const to = decodeStatus(raw.slice(separatorIndex + 1));
  if (!from || !to) {
    return undefined;
  }
  return { from, to };
}

/** Drop invalid/duplicate pairs; keep first-seen order. */
function normalizeStatusPairs(
  pairs: readonly CompareStatusPair[],
): CompareStatusPair[] {
  const seen = new Set<string>();
  const normalized: CompareStatusPair[] = [];
  for (const pair of pairs) {
    if (!isCompareItemStatus(pair.from) || !isCompareItemStatus(pair.to)) {
      continue;
    }
    const key = serializeStatusPair(pair);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    normalized.push({ from: pair.from, to: pair.to });
  }
  return normalized;
}

export function serializeStatusPairs(
  pairs: readonly CompareStatusPair[],
): string[] {
  const normalized = normalizeStatusPairs(pairs);
  if (normalized.length === 0) {
    return [compareEmptyStatusPairsToken];
  }
  return normalized.map(serializeStatusPair);
}

export function parseStatusPairs(
  values: readonly string[],
): CompareStatusPair[] {
  if (
    values.length === 0 ||
    (values.length === 1 && values[0] === compareEmptyStatusPairsToken)
  ) {
    return [];
  }
  return normalizeStatusPairs(
    values.flatMap(value => {
      const pair = parseStatusPair(value);
      return pair ? [pair] : [];
    }),
  );
}

/** URL wins when present; otherwise stored tokens; otherwise the hardcoded default. */
export function resolveStatusPairs(
  url: readonly string[] | undefined,
  stored: readonly string[] | undefined,
): CompareStatusPair[] {
  if (url !== undefined) {
    return parseStatusPairs(url);
  }
  if (stored !== undefined) {
    return parseStatusPairs(stored);
  }
  return parseStatusPairs(compareDefaultStatusPairParams);
}

export function readStoredStatusPairs(): string[] | undefined {
  try {
    const raw = window.localStorage.getItem(compareStatusPairStorageKey);
    if (raw === null) {
      return undefined;
    }
    const parsed: unknown = JSON.parse(raw);
    if (
      !Array.isArray(parsed) ||
      parsed.some(item => typeof item !== 'string')
    ) {
      return undefined;
    }
    return parsed;
  } catch {
    return undefined;
  }
}

export function writeStoredStatusPairs(values: readonly string[]): void {
  try {
    window.localStorage.setItem(
      compareStatusPairStorageKey,
      JSON.stringify(values),
    );
  } catch {
    // Quota / private mode: in-memory + URL still work.
  }
}

/** Empty list shows all rows; otherwise a row matches any selected (from, to) pair. */
export function applyStatusPairFilter<
  T extends { sideA: CompareItemStatus; sideB: CompareItemStatus },
>(rows: T[], pairs: readonly CompareStatusPair[]): T[] {
  if (pairs.length === 0) {
    return rows;
  }
  return rows.filter(row =>
    pairs.some(pair => pair.from === row.sideA && pair.to === row.sideB),
  );
}
