import { daysToSeconds } from '@/utils/date';
import type { TFilter } from '@/types/general';

export type KcidevCommand = {
  id: string;
  label: string;
  argv: readonly string[];
  omittedFilters: readonly string[];
  reproduction: 'exact' | 'partial';
  variants?: readonly KcidevCommandVariant[];
};

export type KcidevCommandVariant = {
  id: 'human' | 'json' | 'download' | 'gate' | 'gate-json';
  label: string;
  argv: readonly string[];
  writesFiles?: boolean;
};

export type DashboardFilters = {
  architectures?: readonly string[];
  configs?: readonly string[];
  compilers?: readonly string[];
  hardware?: readonly string[];
  testPaths?: readonly string[];
  bootOrigins?: readonly string[];
  minDuration?: number;
  maxDuration?: number;
  statuses?: readonly string[];
  labs?: readonly string[];
  issueAssociations?: readonly string[];
  issueCulprits?: readonly string[];
  issueCategories?: readonly string[];
  issueOptions?: readonly string[];
  hasExactDateBoundaries?: boolean;
  hasTextSearch?: boolean;
  hasTreeCompareStatusPairs?: boolean;
  hasHardwareDateWindow?: boolean;
};

export type TranslatedFilters = {
  argv: readonly string[];
  omittedFilters: readonly string[];
  reproduction: 'exact' | 'partial';
};

const singleValueMappings = [
  ['architectures', '--arch', 'architecture'],
  ['configs', '--config', 'config'],
  ['compilers', '--compiler', 'compiler'],
  ['hardware', '--hardware', 'hardware'],
  ['testPaths', '--test-path', 'boot/test path'],
  ['bootOrigins', '--boot-origin', 'boot origin'],
] as const;

/** Translate only filters whose dashboard and kci-dev handler semantics agree. */
export const translateDashboardFilters = (
  filters: DashboardFilters,
): TranslatedFilters => {
  const argv: string[] = [];
  const omitted: string[] = [];
  for (const [key, option, label] of singleValueMappings) {
    const values = filters[key] ?? [];
    if (values.length === 1) {
      argv.push(option, values[0]);
    } else if (values.length > 1) {
      omitted.push(`${label} (multiple values)`);
    }
  }
  if (filters.minDuration !== undefined) {
    argv.push('--min-duration', String(filters.minDuration));
  }
  if (filters.maxDuration !== undefined) {
    argv.push('--max-duration', String(filters.maxDuration));
  }

  // kci-dev groups statuses differently from the dashboard, so this is
  // deliberately disclosed rather than translated to a misleading command.
  if ((filters.statuses?.length ?? 0) > 0) {
    omitted.push('status');
  }
  const unsupported: Array<[boolean, string]> = [
    [(filters.labs?.length ?? 0) > 0, 'lab'],
    [(filters.issueAssociations?.length ?? 0) > 0, 'issue association'],
    [(filters.issueCulprits?.length ?? 0) > 0, 'issue culprit'],
    [(filters.issueCategories?.length ?? 0) > 0, 'issue category'],
    [(filters.issueOptions?.length ?? 0) > 0, 'issue options'],
    [filters.hasExactDateBoundaries === true, 'exact custom date boundaries'],
    [filters.hasTextSearch === true, 'client-side text search'],
    [filters.hasTreeCompareStatusPairs === true, 'Tree Compare status pairs'],
    [filters.hasHardwareDateWindow === true, 'hardware date window'],
  ];
  unsupported.forEach(([present, label]) => present && omitted.push(label));
  const omittedFilters = [...new Set(omitted)];
  return {
    argv,
    omittedFilters,
    reproduction: omittedFilters.length === 0 ? 'exact' : 'partial',
  };
};

const enabledValues = (value: unknown): string[] =>
  value && typeof value === 'object'
    ? Object.entries(value)
        .filter(([, enabled]) => enabled === true)
        .map(([key]) => key)
    : [];

export const dashboardFiltersFromDiffFilter = (
  diffFilter: TFilter,
  result: 'builds' | 'boots' | 'tests',
): DashboardFilters => {
  const durationPrefix = result.slice(0, -1) as 'build' | 'boot' | 'test';
  const record = diffFilter as Record<string, unknown>;
  return {
    architectures: enabledValues(record.archs),
    configs: enabledValues(record.configs),
    compilers: enabledValues(record.compilers),
    hardware: enabledValues(record.hardware),
    testPaths: enabledValues(
      result === 'boots' ? record.bootPath : record.testPath,
    ),
    bootOrigins: enabledValues(record.bootOrigin),
    minDuration: record[`${durationPrefix}DurationMin`] as number | undefined,
    maxDuration: record[`${durationPrefix}DurationMax`] as number | undefined,
    statuses: enabledValues(record[`${durationPrefix}Status`]),
    labs: enabledValues(record.labs),
    issueAssociations: enabledValues(record[`${durationPrefix}Issue`]),
    issueCulprits: enabledValues(record.issueCulprits),
    issueCategories: enabledValues(record.issueCategories),
    issueOptions: enabledValues(record.issueOptions),
  };
};

type CommonOptions = {
  omittedFilters?: readonly string[];
  filters?: DashboardFilters;
};

type TreeResultsOptions = CommonOptions & {
  origin?: string;
  gitUrl?: string;
  branch?: string;
  commit?: string;
};

type HardwareResultsOptions = CommonOptions & {
  name?: string;
  origin?: string;
};

type IssueListingOptions = CommonOptions & {
  origins: readonly string[];
  days?: number;
};

type IssueListingState = {
  selectedOrigins: Readonly<Record<string, boolean>>;
  availableOrigins: readonly string[];
  defaultDays: number;
  startTimestampInSeconds?: number;
  endTimestampInSeconds?: number;
  hasCulpritFilter: boolean;
  hasCategoryFilter: boolean;
  hasIncidentFilter: boolean;
  hasTextSearch: boolean;
};

type TreeCompareOptions = CommonOptions & {
  origin?: string;
  gitUrl?: string;
  branch?: string;
  hashA?: string;
  hashB?: string;
};

const baseArgv = ['kci-dev', 'results'] as const;

const command = (
  id: string,
  label: string,
  argv: readonly string[],
  omittedFilters: readonly string[] = [],
  variants?: readonly KcidevCommandVariant[],
): KcidevCommand => {
  const result: KcidevCommand = {
    id,
    label,
    argv,
    omittedFilters: [...new Set(omittedFilters)],
    reproduction: omittedFilters.length === 0 ? 'exact' : 'partial',
  };
  result.variants = variants ?? standardVariants(argv);
  return result;
};

const standardVariants = (
  argv: readonly string[],
  options: { download?: boolean; formatJson?: boolean } = {},
): KcidevCommandVariant[] => [
  { id: 'human', label: 'Human-readable', argv },
  {
    id: 'json',
    label: 'JSON',
    argv: [
      ...argv,
      ...(options.formatJson ? ['--format', 'json'] : ['--json']),
    ],
  },
  ...(options.download
    ? ([
        {
          id: 'download',
          label: 'Download logs (writes files)',
          argv: [...argv, '--download-logs'],
          writesFiles: true,
        },
      ] satisfies KcidevCommandVariant[])
    : []),
];

const appendOption = (argv: string[], option: string, value?: string): void => {
  if (value !== undefined) {
    argv.push(option, value);
  }
};

export const createTreeListingCommand = ({
  origin,
  days,
  omittedFilters,
}: CommonOptions & {
  origin?: string;
  days?: number;
}): KcidevCommand | undefined => {
  if (origin === undefined || days === undefined) {
    return undefined;
  }

  return command(
    'trees',
    'Tree listing',
    [...baseArgv, 'trees', '--origin', origin, '--days', String(days)],
    omittedFilters,
  );
};

export const createTreeResultsCommand = (
  result: 'builds' | 'boots' | 'tests',
  {
    origin,
    gitUrl,
    branch,
    commit,
    omittedFilters,
    filters,
  }: TreeResultsOptions,
): KcidevCommand | undefined => {
  if (origin === undefined || commit === undefined) {
    return undefined;
  }

  const argv = [...baseArgv, result, '--origin', origin];
  appendOption(argv, '--giturl', gitUrl);
  appendOption(argv, '--branch', branch);
  argv.push('--commit', commit);
  const translated = translateDashboardFilters(filters ?? {});
  argv.push(...translated.argv);
  return command(`tree-${result}`, `Tree ${result}`, argv, [
    ...(omittedFilters ?? []),
    ...translated.omittedFilters,
  ]);
};

export const createResultDetailsCommand = (
  result: 'build' | 'boot' | 'test',
  id?: string,
  omittedFilters: readonly string[] = [],
): KcidevCommand | undefined =>
  id === undefined
    ? undefined
    : command(
        `${result}-details`,
        `${result} details`,
        [...baseArgv, result, '--id', id],
        omittedFilters,
        standardVariants([...baseArgv, result, '--id', id], { download: true }),
      );

export const createIssueDetailsCommand = ({
  id,
  origin,
  omittedFilters,
}: CommonOptions & {
  id?: string;
  origin?: string;
}): KcidevCommand | undefined => {
  if (!id || !origin) {
    return undefined;
  }

  return command(
    'issue-details',
    'Issue details',
    [...baseArgv, 'issue', '--id', id, '--origin', origin],
    omittedFilters,
  );
};

export const createIssueListingCommands = ({
  origins,
  days,
  omittedFilters,
}: IssueListingOptions): KcidevCommand[] => {
  if (days === undefined) {
    return [];
  }

  return origins.map(origin =>
    command(
      `issues-${origin}`,
      `Issues from ${origin}`,
      [...baseArgv, 'issues', '--origin', origin, '--days', String(days)],
      omittedFilters,
    ),
  );
};

export const createIssueListingCommandsFromState = ({
  selectedOrigins,
  availableOrigins,
  defaultDays,
  startTimestampInSeconds,
  endTimestampInSeconds,
  hasCulpritFilter,
  hasCategoryFilter,
  hasIncidentFilter,
  hasTextSearch,
}: IssueListingState): KcidevCommand[] => {
  const selected = Object.entries(selectedOrigins)
    .filter(([, enabled]) => enabled)
    .map(([origin]) => origin);
  const customRange =
    startTimestampInSeconds !== undefined ||
    endTimestampInSeconds !== undefined;
  const days =
    startTimestampInSeconds !== undefined && endTimestampInSeconds !== undefined
      ? Math.max(
          1,
          Math.ceil(
            (endTimestampInSeconds - startTimestampInSeconds) /
              daysToSeconds(1),
          ),
        )
      : defaultDays;
  const omittedFilters = [
    ...(customRange ? ['exact start and end boundaries'] : []),
    ...(hasCulpritFilter ? ['issue culprit'] : []),
    ...(hasCategoryFilter ? ['issue category'] : []),
    ...(hasIncidentFilter ? ['incident'] : []),
    ...(hasTextSearch ? ['text search'] : []),
  ];

  return createIssueListingCommands({
    origins: selected.length > 0 ? selected : availableOrigins,
    days,
    omittedFilters,
  });
};

export const createTreeCompareCommand = ({
  origin,
  gitUrl,
  branch,
  hashA,
  hashB,
  omittedFilters,
}: TreeCompareOptions): KcidevCommand | undefined => {
  if (!origin || !gitUrl || !branch || !hashA || !hashB) {
    return undefined;
  }

  const argv = [
    ...baseArgv,
    'compare',
    '--origin',
    origin,
    '--giturl',
    gitUrl,
    '--branch',
    branch,
    hashA,
    hashB,
  ];
  const gateArgv = [
    ...baseArgv,
    'gate',
    '--origin',
    origin,
    '--giturl',
    gitUrl,
    '--branch',
    branch,
    '--base',
    hashA,
    '--head',
    hashB,
  ];
  return command('tree-compare', 'Tree comparison', argv, omittedFilters, [
    ...standardVariants(argv, { formatJson: true }),
    { id: 'gate', label: 'CI gate', argv: gateArgv },
    {
      id: 'gate-json',
      label: 'CI gate (JSON)',
      argv: [...gateArgv, '--format', 'json'],
    },
  ]);
};

export const createHardwareListingCommand = ({
  origin,
  omittedFilters,
}: CommonOptions & { origin?: string }): KcidevCommand | undefined =>
  origin === undefined
    ? undefined
    : command(
        'hardware-list',
        'Hardware listing',
        [...baseArgv, 'hardware', 'list', '--origin', origin],
        omittedFilters,
      );

export const createHardwareResultsCommand = (
  result: 'builds' | 'boots' | 'tests',
  { name, origin, omittedFilters, filters }: HardwareResultsOptions,
): KcidevCommand | undefined => {
  if (name === undefined || origin === undefined) {
    return undefined;
  }

  const translated = translateDashboardFilters(filters ?? {});
  return command(
    `hardware-${result}`,
    `Hardware ${result}`,
    [
      ...baseArgv,
      'hardware',
      result,
      '--name',
      name,
      '--origin',
      origin,
      ...translated.argv,
    ],
    [...(omittedFilters ?? []), ...translated.omittedFilters],
  );
};

const safeShellWord = /^[A-Za-z0-9_@%+=:,./-]+$/;

export const serializeShellArgv = (argv: readonly string[]): string =>
  argv
    .map(value =>
      safeShellWord.test(value) ? value : `'${value.replace(/'/g, `'"'"'`)}'`,
    )
    .join(' ');

export const serializeKcidevCommand = (value: KcidevCommand): string =>
  serializeShellArgv(value.argv);
