import { describe, expect, it } from 'vitest';

import type { TestHistory } from '@/types/general';
import type { Status } from '@/types/database';

import { buildTestsTree } from './buildTestsTree';
import { collapseSingleChildChains } from './collapseTestsTree';
import { buildUnifiedTestsTree } from './buildUnifiedTestsTree';
import type { UnifiedTestRow } from './types';

const PASS = 'PASS' as Status;

function testAt(path: string, id = path): TestHistory {
  return {
    id,
    path,
    status: PASS,
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
        A: [{ 'I.L': ['P', 'Q'] }, 'J.M'],
      },
      'B.I',
    ]);
  });

  it('keeps a group when it wraps multiple tests at the same path', () => {
    const tree = collapseSingleChildChains(
      buildTestsTree([testAt('A.X', 'a1'), testAt('A.X', 'a2')]),
    );

    const unified = buildUnifiedTestsTree(tree);

    // A → X collapses to A.X; the group is kept because it has two tests
    expect(summarize(unified)).toEqual([
      {
        'A.X': ['', ''],
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
        'A.M': ['X', 'Y.P'],
      },
    ]);
  });
});
