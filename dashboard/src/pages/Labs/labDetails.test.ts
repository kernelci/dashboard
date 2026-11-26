import { describe, expect, it } from 'vitest';

import type { RequiredStatusCount } from '@/types/general';
import type { LabDetailsTree } from '@/types/labDetails';

import { attentionLines, checkedTreeParams, sumLabTrees } from './labDetails';

const count = (pass: number, fail = 0): RequiredStatusCount => ({
  PASS: pass,
  FAIL: fail,
  ERROR: 0,
  MISS: 0,
  SKIP: 0,
  DONE: 0,
  NULL: 0,
});

const tree = (key: string, pass: number, dayPass: number): LabDetailsTree => ({
  key,
  tree_name: key,
  git_branch: 'master',
  builds: count(pass),
  boots: count(0),
  tests: count(0),
  build_issues: [
    {
      id: 'issue-1',
      version: 1,
      incidents_info: count(0, 1),
    },
  ],
  boot_issues: [],
  test_issues: [],
  daily: {
    builds: [
      {
        day: '2026-11-01',
        pass_count: dayPass,
        fail_count: 0,
        inconclusive_count: 0,
      },
    ],
    boots: [],
    tests: [],
  },
});

describe('labDetails', () => {
  it('sums the checked trees and hides an empty attention list', () => {
    const one = sumLabTrees([tree('a', 1, 1)]);
    expect(one.builds.PASS).toBe(1);
    expect(one.daily.builds).toEqual([
      {
        day: '2026-11-01',
        pass_count: 1,
        fail_count: 0,
        inconclusive_count: 0,
      },
    ]);
    expect(one.buildIssues).toHaveLength(1);

    const both = sumLabTrees([tree('a', 1, 1), tree('b', 1, 1)]);
    expect(both.builds.PASS).toBe(2);
    expect(both.daily.builds[0]?.pass_count).toBe(2);
    expect(both.buildIssues).toHaveLength(1);
    expect(both.buildIssues[0]?.incidents_info.FAIL).toBe(2);

    expect(checkedTreeParams(2, ['a', 'b'])).toBeUndefined();
    expect(checkedTreeParams(2, ['b'])).toEqual(['b']);

    expect(attentionLines([])).toBeNull();
    expect(
      attentionLines([
        { kind: 'boot', path: null },
        { kind: 'test', path: 'kselftest' },
      ]),
    ).toEqual(['boot', 'kselftest']);
  });
});
