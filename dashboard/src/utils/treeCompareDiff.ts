import type {
  CompareBootFailureRow,
  CompareBuildFailureRow,
  CompareChangeFilter,
  CompareChangeType,
  CompareGroupedApiStatus,
  CompareItemStatus,
  CompareTestFailureRow,
  TreeCompareBuildDiffApiRow,
  TreeCompareTestDiffApiRow,
} from '@/types/tree/TreeCompare';
import { compareChangeFilters } from '@/types/tree/TreeCompare';

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
): CompareChangeType {
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
      idA: row.id_a ?? null,
      idB: row.id_b ?? null,
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
      idA: row.id_a ?? null,
      idB: row.id_b ?? null,
    };
  });
}

/** Keep URL/search order stable and drop unknown values. */
export function normalizeChangeFilters(
  filters: readonly CompareChangeFilter[],
): CompareChangeFilter[] {
  return compareChangeFilters.filter(filter => filters.includes(filter));
}

export function toggleChangeFilter(
  current: readonly CompareChangeFilter[],
  value: CompareChangeFilter,
): CompareChangeFilter[] {
  const next = current.includes(value)
    ? current.filter(filter => filter !== value)
    : [...current, value];
  return normalizeChangeFilters(next);
}

/**
 * Empty selection or every chip selected both mean "show all" — same as
 * former "All changes". Partial selection keeps matching change types.
 */
export function applyChangeFilter<T extends { change: CompareChangeType }>(
  rows: T[],
  changeFilter: readonly CompareChangeFilter[],
): T[] {
  if (changeFilter.length === 0) {
    return rows;
  }
  const selected = new Set<string>(changeFilter);
  return rows.filter(row => selected.has(row.change));
}
