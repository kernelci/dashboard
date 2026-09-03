export type KcidevCommand = {
  id: string;
  label: string;
  argv: readonly string[];
  omittedFilters: readonly string[];
};

type CommonOptions = {
  omittedFilters?: readonly string[];
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

const baseArgv = ['kci-dev', 'results'] as const;

const command = (
  id: string,
  label: string,
  argv: readonly string[],
  omittedFilters: readonly string[] = [],
): KcidevCommand => ({ id, label, argv, omittedFilters });

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
  { origin, gitUrl, branch, commit, omittedFilters }: TreeResultsOptions,
): KcidevCommand | undefined => {
  if (origin === undefined || commit === undefined) {
    return undefined;
  }

  const argv = [...baseArgv, result, '--origin', origin];
  appendOption(argv, '--giturl', gitUrl);
  appendOption(argv, '--branch', branch);
  argv.push('--commit', commit);
  return command(`tree-${result}`, `Tree ${result}`, argv, omittedFilters);
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
      );

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
  { name, origin, omittedFilters }: HardwareResultsOptions,
): KcidevCommand | undefined => {
  if (name === undefined || origin === undefined) {
    return undefined;
  }

  return command(
    `hardware-${result}`,
    `Hardware ${result}`,
    [...baseArgv, 'hardware', result, '--name', name, '--origin', origin],
    omittedFilters,
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
