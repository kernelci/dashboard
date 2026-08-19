import { describe, expect, it } from 'vitest';

import type { TestHistory } from '@/types/general';
import type { Status } from '@/types/database';
import { UNKNOWN_STRING } from '@/utils/constants/backend';

import { buildTestsTree } from './buildTestsTree';
import { collapseSingleChildChains } from './collapseTestsTree';
import { buildUnifiedTestsTree } from './buildUnifiedTestsTree';
import { buildGroupSummaries, getDateSortKey } from './groupSummaries';
import type { UnifiedTestRow } from './types';

const PASS = 'PASS' as Status;

function testAt(
  path: string,
  id = path,
  extras: Partial<TestHistory> = {},
): TestHistory {
  return {
    id,
    path,
    status: PASS,
    ...extras,
  };
}

function summarize(rows: UnifiedTestRow[]): unknown {
  return rows.map(row => {
    if (row.kind === 'leaf') {
      return row.path;
    }
    return { [row.path]: summarize(row.subRows ?? []) };
  });
}

describe('collapseSingleChildChains + buildUnifiedTestsTree', () => {
  it('collapses single-child chains and single-test leaf groups', () => {
    const tree = collapseSingleChildChains(
      buildTestsTree([
        testAt('A.I.L.P'),
        testAt('A.I.L.Q'),
        testAt('A.J.M'),
        testAt('B.I'),
      ]),
    );

    const unified = buildUnifiedTestsTree(tree);

    expect(summarize(unified)).toEqual([
      {
        A: [{ 'I.L': ['A.I.L.P', 'A.I.L.Q'] }, 'A.J.M'],
      },
      'B.I',
    ]);
  });

  it('keeps a group when it wraps multiple tests at the same path', () => {
    const tree = collapseSingleChildChains(
      buildTestsTree([testAt('A.X', 'a1'), testAt('A.X', 'a2')]),
    );

    const unified = buildUnifiedTestsTree(tree);

    expect(summarize(unified)).toEqual([
      {
        'A.X': ['A.X', 'A.X'],
      },
    ]);
  });

  it('omits intermediate groups with a single item (A.M.X + A.M.Y.P)', () => {
    const tree = collapseSingleChildChains(
      buildTestsTree([testAt('A.M.X'), testAt('A.M.Y.P')]),
    );

    const unified = buildUnifiedTestsTree(tree);

    expect(summarize(unified)).toEqual([
      {
        'A.M': ['A.M.X', 'A.M.Y.P'],
      },
    ]);
  });
});

describe('buildGroupSummaries', () => {
  const leaf = (
    overrides: Partial<UnifiedTestRow> & { id: string },
  ): UnifiedTestRow => ({
    kind: 'leaf',
    path: overrides.path ?? overrides.id,
    done_tests: 0,
    error_tests: 0,
    fail_tests: 0,
    miss_tests: 0,
    pass_tests: 1,
    skip_tests: 0,
    null_tests: 0,
    total_tests: 1,
    ...overrides,
  });

  it('marks uniform values and mixed counts', () => {
    const summaries = buildGroupSummaries([
      leaf({ id: '1', hardware: ['hw-a'], duration: '1s', lab: 'lab-b' }),
      leaf({ id: '2', hardware: ['hw-a'], duration: '2s', lab: 'lab-a' }),
    ]);

    expect(summaries.hardware).toEqual({ kind: 'uniform', value: ['hw-a'] });
    expect(summaries.duration).toEqual({ kind: 'mixed', count: 2 });
    expect(summaries.lab).toEqual({ kind: 'mixed', count: 2 });
  });

  it('counts unique child labs', () => {
    const summaries = buildGroupSummaries([
      leaf({ id: '1', lab: 'z-lab' }),
      leaf({ id: '2', lab: 'a-lab' }),
      leaf({ id: '3', lab: 'z-lab' }),
    ]);

    expect(summaries.lab).toEqual({ kind: 'mixed', count: 2 });
  });

  it('counts Unknown as a distinct lab', () => {
    const summaries = buildGroupSummaries([
      leaf({ id: '1', lab: 'lab-a' }),
      leaf({ id: '2' }),
    ]);

    expect(summaries.lab).toEqual({ kind: 'mixed', count: 2 });
  });

  it('shows Unknown when all child labs are missing', () => {
    const summaries = buildGroupSummaries([
      leaf({ id: '1' }),
      leaf({ id: '2' }),
    ]);

    expect(summaries.lab).toEqual({
      kind: 'uniform',
      value: UNKNOWN_STRING,
    });
  });

  it('builds a date range from distinct start times', () => {
    const summaries = buildGroupSummaries([
      leaf({ id: '1', start_time: '2024-01-01T10:00:00Z' }),
      leaf({ id: '2', start_time: '2024-01-03T10:00:00Z' }),
      leaf({ id: '3', start_time: '2024-01-02T10:00:00Z' }),
    ]);

    expect(summaries.start_time).toEqual({
      kind: 'dateRange',
      min: '2024-01-01T10:00:00Z',
      max: '2024-01-03T10:00:00Z',
    });
  });

  it('keeps a uniform date when all start times match', () => {
    const summaries = buildGroupSummaries([
      leaf({ id: '1', start_time: '2024-01-01T10:00:00Z' }),
      leaf({ id: '2', start_time: '2024-01-01T10:00:00Z' }),
    ]);

    expect(summaries.start_time).toEqual({
      kind: 'uniform',
      value: '2024-01-01T10:00:00Z',
    });
  });
});

describe('group summaries on unified tree', () => {
  it('attaches summaries to group rows', () => {
    const tree = collapseSingleChildChains(
      buildTestsTree([
        testAt('A.X', 'a1', {
          start_time: '2024-01-01T00:00:00Z',
          lab: 'lab-a',
        }),
        testAt('A.X', 'a2', {
          start_time: '2024-01-02T00:00:00Z',
          lab: 'lab-b',
        }),
      ]),
    );

    const [group] = buildUnifiedTestsTree(tree);
    expect(group.kind).toBe('group');
    expect(group.summaries?.lab).toEqual({ kind: 'mixed', count: 2 });
    expect(group.summaries?.start_time).toEqual({
      kind: 'dateRange',
      min: '2024-01-01T00:00:00Z',
      max: '2024-01-02T00:00:00Z',
    });
  });
});

describe('getDateSortKey', () => {
  it('uses min for oldest-first and max for newest-first on date ranges', () => {
    const group: UnifiedTestRow = {
      id: 'g',
      kind: 'group',
      path: 'A',
      done_tests: 0,
      error_tests: 0,
      fail_tests: 0,
      miss_tests: 0,
      pass_tests: 2,
      skip_tests: 0,
      null_tests: 0,
      total_tests: 2,
      summaries: {
        start_time: {
          kind: 'dateRange',
          min: '2024-01-01T00:00:00Z',
          max: '2024-01-02T00:00:00Z',
        },
      },
    };

    expect(getDateSortKey(group, false)).toBe('2024-01-01T00:00:00Z');
    expect(getDateSortKey(group, true)).toBe('2024-01-02T00:00:00Z');
  });

  it('uses the leaf start_time directly', () => {
    const leaf: UnifiedTestRow = {
      id: 'l',
      kind: 'leaf',
      path: 'A.X',
      done_tests: 0,
      error_tests: 0,
      fail_tests: 0,
      miss_tests: 0,
      pass_tests: 1,
      skip_tests: 0,
      null_tests: 0,
      total_tests: 1,
      start_time: '2024-01-05T00:00:00Z',
    };

    expect(getDateSortKey(leaf, false)).toBe('2024-01-05T00:00:00Z');
    expect(getDateSortKey(leaf, true)).toBe('2024-01-05T00:00:00Z');
  });
});
