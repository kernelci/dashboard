import type { RequiredStatusCount } from '@/types/general';
import type { TIssue } from '@/types/issues';
import type {
  LabAttentionItem,
  LabDailyPoint,
  LabDailySeries,
  LabDetailsTree,
  LabIssue,
} from '@/types/labDetails';

const STATUS_FIELDS = [
  'PASS',
  'FAIL',
  'ERROR',
  'MISS',
  'SKIP',
  'DONE',
  'NULL',
] as const satisfies readonly (keyof RequiredStatusCount)[];

export const toStatusCount = (
  count: Partial<RequiredStatusCount> | null | undefined,
): RequiredStatusCount => {
  const total: RequiredStatusCount = {
    PASS: 0,
    FAIL: 0,
    ERROR: 0,
    MISS: 0,
    SKIP: 0,
    DONE: 0,
    NULL: 0,
  };
  if (!count) {
    return total;
  }
  STATUS_FIELDS.forEach(field => {
    total[field] = count[field] ?? 0;
  });
  return total;
};

const sumStatusCounts = (
  counts: Partial<RequiredStatusCount>[],
): RequiredStatusCount =>
  counts.reduce<RequiredStatusCount>((total, count) => {
    const item = toStatusCount(count);
    return {
      PASS: total.PASS + item.PASS,
      FAIL: total.FAIL + item.FAIL,
      ERROR: total.ERROR + item.ERROR,
      MISS: total.MISS + item.MISS,
      SKIP: total.SKIP + item.SKIP,
      DONE: total.DONE + item.DONE,
      NULL: total.NULL + item.NULL,
    };
  }, toStatusCount(undefined));

const toIssue = (issue: LabIssue): TIssue => ({
  id: issue.id,
  version: issue.version,
  comment: issue.comment ?? undefined,
  report_url: issue.report_url ?? undefined,
  incidents_info: toStatusCount(issue.incidents_info),
});

const sumIssues = (groups: LabIssue[][]): TIssue[] => {
  const merged = new Map<string, TIssue>();
  groups.flat().forEach(raw => {
    const issue = toIssue(raw);
    const key = `${issue.id}@${issue.version}`;
    const existing = merged.get(key);
    if (!existing) {
      merged.set(key, issue);
      return;
    }
    existing.incidents_info = sumStatusCounts([
      existing.incidents_info,
      issue.incidents_info,
    ]);
  });
  return [...merged.values()];
};

const sumDaily = (series: LabDailyPoint[][]): LabDailyPoint[] => {
  const byDay = new Map<string, LabDailyPoint>();
  series.flat().forEach(point => {
    const current = byDay.get(point.day);
    if (!current) {
      byDay.set(point.day, { ...point });
      return;
    }
    current.pass_count += point.pass_count;
    current.fail_count += point.fail_count;
    current.inconclusive_count += point.inconclusive_count;
  });
  return [...byDay.values()].sort((left, right) =>
    left.day.localeCompare(right.day),
  );
};

type LabTreeSummary = {
  builds: RequiredStatusCount;
  boots: RequiredStatusCount;
  tests: RequiredStatusCount;
  buildIssues: TIssue[];
  bootIssues: TIssue[];
  testIssues: TIssue[];
  daily: LabDailySeries;
};

export const sumLabTrees = (trees: LabDetailsTree[]): LabTreeSummary => ({
  builds: sumStatusCounts(trees.map(tree => tree.builds)),
  boots: sumStatusCounts(trees.map(tree => tree.boots)),
  tests: sumStatusCounts(trees.map(tree => tree.tests)),
  buildIssues: sumIssues(trees.map(tree => tree.build_issues)),
  bootIssues: sumIssues(trees.map(tree => tree.boot_issues)),
  testIssues: sumIssues(trees.map(tree => tree.test_issues)),
  daily: {
    builds: sumDaily(trees.map(tree => tree.daily.builds)),
    boots: sumDaily(trees.map(tree => tree.daily.boots)),
    tests: sumDaily(trees.map(tree => tree.daily.tests)),
  },
});

export const checkedTreeParams = (
  treeCount: number,
  selectedKeys: string[],
): string[] | undefined => {
  if (selectedKeys.length === treeCount) {
    return undefined;
  }
  return [...selectedKeys].sort();
};

export const attentionLines = (
  items: Pick<LabAttentionItem, 'kind' | 'path'>[],
): string[] | null => {
  if (items.length === 0) {
    return null;
  }
  return items.map(item =>
    item.kind === 'boot' ? 'boot' : item.path || 'test',
  );
};
