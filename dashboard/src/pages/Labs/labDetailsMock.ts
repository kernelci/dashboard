import type { Status } from '@/types/database';
import type { RequiredStatusCount, TestHistory } from '@/types/general';
import type { TIssue } from '@/types/issues';

export type LabBuildRow = {
  tree: string;
  branch: string;
  config: string;
  arch: string;
  compiler: string;
  status: Status;
  started: string;
  hasDuration: boolean;
};

export type LabBootRow = {
  tree: string;
  branch: string;
  platform: string;
  config: string;
  arch: string;
  compiler: string;
  status: Status;
  started: string;
  hasDuration: boolean;
  hasLogUrl: boolean;
  hasLogExcerpt: boolean;
};

export type LabTestRow = LabBootRow & {
  path: string;
};

export type LabTreeMock = {
  key: string;
  tree: string;
  branch: string;
  commitName: string;
  commitHash: string;
  builds: RequiredStatusCount;
  boots: RequiredStatusCount;
  tests: RequiredStatusCount;
  buildIssues: TIssue[];
  bootIssues: TIssue[];
  testIssues: TIssue[];
  buildRows: LabBuildRow[];
  bootRows: LabBootRow[];
  testRows: LabTestRow[];
};

const blankCount = (): RequiredStatusCount => ({
  PASS: 0,
  FAIL: 0,
  ERROR: 0,
  MISS: 0,
  SKIP: 0,
  DONE: 0,
  NULL: 0,
});

const countStatus = (
  counts: RequiredStatusCount,
  status: Status,
): RequiredStatusCount => ({
  ...counts,
  [status]: counts[status] + 1,
});

export const sumStatusCounts = (
  counts: RequiredStatusCount[],
): RequiredStatusCount =>
  counts.reduce(
    (total, item) => ({
      PASS: total.PASS + item.PASS,
      FAIL: total.FAIL + item.FAIL,
      ERROR: total.ERROR + item.ERROR,
      MISS: total.MISS + item.MISS,
      SKIP: total.SKIP + item.SKIP,
      DONE: total.DONE + item.DONE,
      NULL: total.NULL + item.NULL,
    }),
    blankCount(),
  );

const countRows = (statuses: Status[]): RequiredStatusCount =>
  statuses.reduce(countStatus, blankCount());

const issueFor = (
  id: string,
  comment: string,
  counts: RequiredStatusCount,
): TIssue[] => {
  if (counts.FAIL + counts.ERROR + counts.MISS === 0) {
    return [];
  }
  return [{ id, version: 1, comment, incidents_info: counts }];
};

const platformsFor = (labName: string): [string, string] => {
  if (labName.includes('renesas')) {
    return ['r8a774b1-hihope-rzg2n-ex', 'r9a07g044l2-smarc-rzg2l'];
  }
  if (labName.includes('qualcomm')) {
    return ['qcs6490-rb3gen2', 'sm8550-hdk'];
  }
  if (labName.includes('baylibre')) {
    return ['meson-g12b-odroid-n2', 'amlogic-sm1'];
  }
  if (labName.includes('broonie')) {
    return ['imx8mm-evk', 'bcm2711-rpi-4-b'];
  }
  return ['qemu-arm64', 'rk3399-rock-pi-4b'];
};

const treeKey = (tree: string, branch: string): string => `${tree}/${branch}`;

export const toTestHistory = (
  rows: LabTestRow[],
  labName: string,
): TestHistory[] =>
  rows.map((row, index) => {
    const [hours, minutes] = row.started.split(':');
    const start = new Date();
    start.setHours(Number(hours), Number(minutes), 0, 0);
    return {
      id: `sample-${index}`,
      status: row.status,
      path: row.path,
      start_time: start.toISOString(),
      tree_name: row.tree,
      git_repository_branch: row.branch,
      lab: labName,
      environment_misc: { platform: row.platform },
    };
  });

export type LabDailyKind = 'builds' | 'boots' | 'tests';

type DailySplit = {
  pass: number[];
  fail: number[];
  inconclusive: number[];
};

// Per-tree sample counts, oldest to newest. The chart sums selected trees.
// Longer windows repeat the pattern.
/* eslint-disable no-magic-numbers -- proposal chart sample, not derived from rows */
const dailyPerTree: Record<LabDailyKind, DailySplit> = {
  builds: {
    pass: [3, 3, 3, 4, 3, 3, 3, 3, 4, 3, 3, 3, 3, 4],
    fail: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    inconclusive: [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
  },
  boots: {
    pass: [6, 6, 6, 7, 6, 6, 6, 7, 6, 6, 6, 6, 7, 6],
    fail: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    inconclusive: [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
  },
  tests: {
    pass: [14, 14, 15, 14, 14, 14, 15, 14, 14, 15, 14, 14, 14, 15],
    fail: [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    inconclusive: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
  },
};
/* eslint-enable no-magic-numbers */

const scaleWindow = (
  pattern: number[],
  days: number,
  treeCount: number,
): number[] => {
  const window =
    days <= pattern.length
      ? pattern.slice(pattern.length - days)
      : Array.from(
          { length: days },
          (_, index) => pattern[index % pattern.length] ?? 0,
        );
  return window.map(value => value * treeCount);
};

export const dailyStatus = (
  kind: LabDailyKind,
  days: number,
  treeCount: number,
): DailySplit => ({
  pass: scaleWindow(dailyPerTree[kind].pass, days, treeCount),
  fail: scaleWindow(dailyPerTree[kind].fail, days, treeCount),
  inconclusive: scaleWindow(dailyPerTree[kind].inconclusive, days, treeCount),
});

type BuildInput = Omit<LabBuildRow, 'tree' | 'branch' | 'hasDuration'>;

type BootInput = Omit<
  LabBootRow,
  'tree' | 'branch' | 'config' | 'hasDuration' | 'hasLogUrl' | 'hasLogExcerpt'
> & { config?: string };

type TestInput = BootInput & Pick<LabTestRow, 'path'>;

const stampBuilds = (
  rows: BuildInput[],
  tree: string,
  branch: string,
): LabBuildRow[] =>
  rows.map((row, index) => ({
    ...row,
    tree,
    branch,
    hasDuration: index === 0 && rows.length > 1,
  }));

/* eslint-disable no-magic-numbers -- sample gaps so the fill rates are not all full */
const stampRuns = <T extends BootInput>(
  rows: T[],
  tree: string,
  branch: string,
): (Omit<T, 'config'> & LabBootRow)[] =>
  rows.map((row, index) => ({
    ...row,
    config: row.config ?? 'defconfig',
    tree,
    branch,
    hasDuration: index % 4 !== 3,
    hasLogUrl: index % 3 !== 2,
    hasLogExcerpt: index % 5 !== 4,
  }));
/* eslint-enable no-magic-numbers */

export type SliceKind = 'named' | 'unknown' | 'other';

export type FrequencySlice = {
  name: string;
  value: number;
  kind: SliceKind;
};

const FREQUENCY_TOP = 8;

export const frequencySlices = (
  labels: readonly string[],
  top = FREQUENCY_TOP,
): FrequencySlice[] => {
  const counts = new Map<string, number>();
  let unknown = 0;
  labels.forEach(label => {
    const name = label.trim();
    if (name === '') {
      unknown += 1;
      return;
    }
    counts.set(name, (counts.get(name) ?? 0) + 1);
  });
  const ranked = [...counts.entries()].sort(
    (left, right) => right[1] - left[1] || left[0].localeCompare(right[0]),
  );
  const named = ranked
    .slice(0, top)
    .map(([name, value]): FrequencySlice => ({ name, value, kind: 'named' }));
  const other = ranked
    .slice(top)
    .reduce((total, [, value]) => total + value, 0);
  if (other > 0) {
    named.push({ name: '', value: other, kind: 'other' });
  }
  if (unknown > 0) {
    named.push({ name: '', value: unknown, kind: 'unknown' });
  }
  return named;
};

export const fillCount = (
  flags: readonly boolean[],
): { filled: number; total: number } => ({
  filled: flags.filter(Boolean).length,
  total: flags.length,
});

export type FillTone = 'good' | 'mid' | 'bad';

export const FILL_GREEN_AT = 80;
export const FILL_YELLOW_AT = 50;

export const fillTone = (percent: number): FillTone => {
  if (percent >= FILL_GREEN_AT) {
    return 'good';
  }
  if (percent >= FILL_YELLOW_AT) {
    return 'mid';
  }
  return 'bad';
};

const makeTree = ({
  tree,
  branch,
  commitName,
  commitHash,
  buildRows,
  bootRows,
  testRows,
}: {
  tree: string;
  branch: string;
  commitName: string;
  commitHash: string;
  buildRows: BuildInput[];
  bootRows: BootInput[];
  testRows: TestInput[];
}): LabTreeMock => {
  const builds = stampBuilds(buildRows, tree, branch);
  const boots = stampRuns(bootRows, tree, branch);
  const tests = stampRuns(testRows, tree, branch);
  const buildCounts = countRows(builds.map(row => row.status));
  const bootCounts = countRows(boots.map(row => row.status));
  const testCounts = countRows(tests.map(row => row.status));

  return {
    key: treeKey(tree, branch),
    tree,
    branch,
    commitName,
    commitHash,
    builds: buildCounts,
    boots: bootCounts,
    tests: testCounts,
    buildIssues: issueFor(
      `sample:${tree}:build`,
      `${tree} build failures`,
      buildCounts,
    ),
    bootIssues: issueFor(
      `sample:${tree}:boot`,
      `${tree} boot failures`,
      bootCounts,
    ),
    testIssues: issueFor(
      `sample:${tree}:test`,
      `${tree} test failures`,
      testCounts,
    ),
    buildRows: builds,
    bootRows: boots,
    testRows: tests,
  };
};

const SPREAD_PLATFORMS = [
  '',
  'qemu-arm64',
  'rk3399-rock-pi-4b',
  'imx8mm-evk',
  'bcm2711-rpi-4-b',
  'meson-g12b-odroid-n2',
  'amlogic-sm1',
  'qcs6490-rb3gen2',
  'sm8550-hdk',
  'jh7110-visionfive-2',
];

const SPREAD_CONFIGS = [
  'defconfig',
  'allmodconfig',
  'tinyconfig',
  'allyesconfig',
  'defconfig+thinlto',
  'kvm_guest.config',
  'arm64_defconfig',
  'x86_64_defconfig',
  'riscv_defconfig',
];

const SPREAD_COMPILERS = ['gcc-13', 'gcc-14', 'clang-18', 'clang-19'];
const SPREAD_ARCHS = ['arm64', 'arm', 'x86_64', 'riscv'];
const SPREAD_STATUS: Status[] = ['PASS', 'FAIL', 'MISS', 'ERROR', 'PASS'];

const spreadRuns = (
  primaryPlatform: string,
  secondaryPlatform: string,
): BootInput[] =>
  [...SPREAD_PLATFORMS, primaryPlatform, secondaryPlatform].map(
    (platform, index) => ({
      platform,
      config: SPREAD_CONFIGS[index % SPREAD_CONFIGS.length] ?? 'defconfig',
      arch: SPREAD_ARCHS[index % SPREAD_ARCHS.length] ?? 'arm64',
      compiler: SPREAD_COMPILERS[index % SPREAD_COMPILERS.length] ?? 'gcc-13',
      status: SPREAD_STATUS[index % SPREAD_STATUS.length] ?? 'PASS',
      started: '12:00',
    }),
  );

export const labDetailsMock = (labName: string): LabTreeMock[] => {
  const [primaryPlatform, secondaryPlatform] = platformsFor(labName);
  const spread = spreadRuns(primaryPlatform, secondaryPlatform);

  return [
    makeTree({
      tree: 'mainline',
      branch: 'master',
      commitName: 'v6.17-rc2',
      commitHash: 'aaaa1111bbbb2222cccc3333dddd4444eeee5555',
      buildRows: [
        {
          config: 'defconfig',
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '09:12',
        },
        {
          config: 'allmodconfig',
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'FAIL',
          started: '08:40',
        },
        {
          config: 'defconfig',
          arch: 'x86_64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '08:10',
        },
      ],
      bootRows: [
        {
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '09:40',
        },
        {
          platform: secondaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'FAIL',
          started: '09:18',
        },
        {
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'MISS',
          started: '09:05',
        },
        ...spread,
      ],
      testRows: [
        {
          path: 'v4l2.compliance',
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '10:02',
        },
        {
          path: 'kselftest',
          platform: secondaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'FAIL',
          started: '09:51',
        },
        {
          path: 'kunit',
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'SKIP',
          started: '09:33',
        },
        ...spread.map((row, index) => ({
          ...row,
          path: index % 2 === 0 ? 'kselftest' : 'v4l2.compliance',
        })),
      ],
    }),
    makeTree({
      tree: 'next',
      branch: 'master',
      commitName: 'next-20261012',
      commitHash: 'ffff6666eeee5555dddd4444cccc3333bbbb2222',
      buildRows: [
        {
          config: 'defconfig',
          arch: 'arm64',
          compiler: 'clang-18',
          status: 'ERROR',
          started: '07:15',
        },
        {
          config: 'defconfig',
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '07:02',
        },
      ],
      bootRows: [
        {
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'FAIL',
          started: '08:05',
        },
      ],
      testRows: [
        {
          path: 'kunit',
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'FAIL',
          started: '08:22',
        },
      ],
    }),
    makeTree({
      tree: 'stable',
      branch: 'linux-6.12.y',
      commitName: 'v6.12.48',
      commitHash: '1111aaaa2222bbbb3333cccc4444dddd5555eeee',
      buildRows: [],
      bootRows: [
        {
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '06:44',
        },
      ],
      testRows: [
        {
          path: 'kselftest',
          platform: primaryPlatform,
          arch: 'arm64',
          compiler: 'gcc-13',
          status: 'PASS',
          started: '07:03',
        },
      ],
    }),
  ];
};

const labAttention = [
  {
    test: 'boot',
    platform: 'cd8180-orion-o6',
    tree: 'next',
    branch: 'pending-fixes',
    commitName: 'v7.3-rc6-241-gdcb935319e0eb',
    commitHash: 'dcb935319e0ebfac02fcaec00ce465055bc61b4e',
    config: 'defconfig',
    arch: 'arm64',
    compiler: 'gcc-15',
    date: '5 Oct 2026',
    passedLabs: ['lava-broonie', 'lava-cip'],
  },
  {
    test: 'kselftest',
    platform: 'bcm2711-rpi-4-b',
    tree: 'mainline',
    branch: 'master',
    commitName: 'v7.3-1138-g14c8977403882',
    commitHash: '14c897740388216acd59477a382de327d5e27ba4',
    config: 'defconfig+lab-setup+kselftest',
    arch: 'arm64',
    compiler: 'gcc-14',
    date: '21 Oct 2026',
    passedLabs: ['lava-collabora', 'lava-cip', 'lava-renesas'],
  },
];

export const labAttentionItems = (labName: string): typeof labAttention => {
  const name = labName.toLowerCase();
  return name.includes('pull-labs-demo') || name.includes('broonie')
    ? labAttention
    : [];
};

export const aggregateLabTrees = (
  trees: LabTreeMock[],
): {
  builds: RequiredStatusCount;
  boots: RequiredStatusCount;
  tests: RequiredStatusCount;
  buildIssues: TIssue[];
  bootIssues: TIssue[];
  testIssues: TIssue[];
  buildRows: LabBuildRow[];
  bootRows: LabBootRow[];
  testRows: LabTestRow[];
} => ({
  builds: sumStatusCounts(trees.map(tree => tree.builds)),
  boots: sumStatusCounts(trees.map(tree => tree.boots)),
  tests: sumStatusCounts(trees.map(tree => tree.tests)),
  buildIssues: trees.flatMap(tree => tree.buildIssues),
  bootIssues: trees.flatMap(tree => tree.bootIssues),
  testIssues: trees.flatMap(tree => tree.testIssues),
  buildRows: trees.flatMap(tree => tree.buildRows),
  bootRows: trees.flatMap(tree => tree.bootRows),
  testRows: trees.flatMap(tree => tree.testRows),
});
