import { describe, expect, it } from 'vitest';

import { daysToSeconds } from '@/utils/date';

import {
  dashboardFiltersFromDiffFilter,
  createHardwareListingCommand,
  createHardwareResultsCommand,
  createIssueDetailsCommand,
  createIssueListingCommands,
  createIssueListingCommandsFromState,
  createResultDetailsCommand,
  createTreeCompareCommand,
  createTreeListingCommand,
  createTreeResultsCommand,
  serializeShellArgv,
} from './kcidevCommand';

describe('kci-dev command generation', () => {
  it('creates a tree listing with the selected origin and days', () => {
    expect(
      createTreeListingCommand({ origin: 'maestro', days: 14 })?.argv,
    ).toEqual([
      'kci-dev',
      'results',
      'trees',
      '--origin',
      'maestro',
      '--days',
      '14',
    ]);
  });

  it.each(['builds', 'boots', 'tests'] as const)(
    'creates tree %s with deterministic, supported flags',
    result => {
      const generated = createTreeResultsCommand(result, {
        origin: 'maestro',
        gitUrl: 'https://example.com/linux.git',
        branch: 'main',
        commit: 'abc123',
      });
      expect(generated?.argv).toEqual([
        'kci-dev',
        'results',
        result,
        '--origin',
        'maestro',
        '--giturl',
        'https://example.com/linux.git',
        '--branch',
        'main',
        '--commit',
        'abc123',
      ]);
      expect(serializeShellArgv(generated!.argv)).not.toContain('--git-url');
    },
  );

  it.each(['build', 'boot', 'test'] as const)('creates %s details', result => {
    expect(createResultDetailsCommand(result, 'result-id')?.argv).toEqual([
      'kci-dev',
      'results',
      result,
      '--id',
      'result-id',
    ]);
  });

  it('creates issue details only when both the id and API origin are available', () => {
    expect(
      createIssueDetailsCommand({
        id: 'issue-id',
        origin: 'maestro',
        omittedFilters: ['issue version'],
      }),
    ).toMatchObject({
      argv: [
        'kci-dev',
        'results',
        'issue',
        '--id',
        'issue-id',
        '--origin',
        'maestro',
      ],
      omittedFilters: ['issue version'],
    });
    expect(createIssueDetailsCommand({ id: 'issue-id' })).toBeUndefined();
    expect(
      createIssueDetailsCommand({ id: 'issue-id', origin: '' }),
    ).toBeUndefined();
  });

  it('creates one labelled issue-listing command per origin', () => {
    expect(
      createIssueListingCommands({
        origins: ['maestro', 'test-origin'],
        days: 5,
        omittedFilters: ['incident', 'text search'],
      }),
    ).toMatchObject([
      {
        id: 'issues-maestro',
        label: 'Issues from maestro',
        argv: [
          'kci-dev',
          'results',
          'issues',
          '--origin',
          'maestro',
          '--days',
          '5',
        ],
        omittedFilters: ['incident', 'text search'],
      },
      {
        id: 'issues-test-origin',
        label: 'Issues from test-origin',
        argv: [
          'kci-dev',
          'results',
          'issues',
          '--origin',
          'test-origin',
          '--days',
          '5',
        ],
        omittedFilters: ['incident', 'text search'],
      },
    ]);
  });

  it('uses selected origins and converts a custom timestamp range to whole days', () => {
    const generated = createIssueListingCommandsFromState({
      selectedOrigins: { maestro: false, selectedA: true, selectedB: true },
      availableOrigins: ['maestro'],
      defaultDays: 5,
      startTimestampInSeconds: 0,
      endTimestampInSeconds: daysToSeconds(1) + 1,
      hasCulpritFilter: true,
      hasCategoryFilter: true,
      hasIncidentFilter: true,
      hasTextSearch: true,
    });

    expect(generated.map(value => value.label)).toEqual([
      'Issues from selectedA',
      'Issues from selectedB',
    ]);
    expect(generated[0]?.argv).toContain('2');
    expect(generated[0]?.omittedFilters).toEqual([
      'exact start and end boundaries',
      'issue culprit',
      'issue category',
      'incident',
      'text search',
    ]);
  });

  it('falls back to API origins and five days for the default date selection', () => {
    const generated = createIssueListingCommandsFromState({
      selectedOrigins: {},
      availableOrigins: ['originA', 'originB'],
      defaultDays: 5,
      hasCulpritFilter: false,
      hasCategoryFilter: false,
      hasIncidentFilter: false,
      hasTextSearch: false,
    });

    expect(generated.map(value => value.argv)).toEqual([
      ['kci-dev', 'results', 'issues', '--origin', 'originA', '--days', '5'],
      ['kci-dev', 'results', 'issues', '--origin', 'originB', '--days', '5'],
    ]);
    expect(generated[0]?.omittedFilters).toEqual([]);
  });

  it('creates a tree comparison with exactly two ordered positional hashes', () => {
    const generated = createTreeCompareCommand({
      origin: 'maestro',
      gitUrl: 'https://example.com/linux.git',
      branch: 'main',
      hashA: 'aaaaaaaa',
      hashB: 'bbbbbbbb',
      omittedFilters: ['status-pair filter'],
    });
    expect(generated?.argv).toEqual([
      'kci-dev',
      'results',
      'compare',
      '--origin',
      'maestro',
      '--giturl',
      'https://example.com/linux.git',
      '--branch',
      'main',
      'aaaaaaaa',
      'bbbbbbbb',
    ]);
    expect(generated?.argv).not.toContain('--latest');
    expect(generated?.omittedFilters).toEqual(['status-pair filter']);
  });

  it('hides a tree comparison until all required values are available', () => {
    expect(
      createTreeCompareCommand({
        origin: 'maestro',
        branch: 'main',
        hashA: 'a',
        hashB: 'b',
      }),
    ).toBeUndefined();
    expect(
      createTreeCompareCommand({
        origin: 'maestro',
        gitUrl: '',
        branch: 'main',
        hashA: 'a',
        hashB: 'b',
      }),
    ).toBeUndefined();
  });

  it('creates a hardware listing', () => {
    expect(createHardwareListingCommand({ origin: 'maestro' })?.argv).toEqual([
      'kci-dev',
      'results',
      'hardware',
      'list',
      '--origin',
      'maestro',
    ]);
  });

  it.each(['builds', 'boots', 'tests'] as const)(
    'creates hardware %s',
    result => {
      expect(
        createHardwareResultsCommand(result, {
          name: 'qemu',
          origin: 'maestro',
        })?.argv,
      ).toEqual([
        'kci-dev',
        'results',
        'hardware',
        result,
        '--name',
        'qemu',
        '--origin',
        'maestro',
      ]);
    },
  );

  it('keeps commands when optional tree values are missing', () => {
    const generated = createTreeResultsCommand('builds', {
      origin: 'maestro',
      commit: 'abc123',
      omittedFilters: ['tableFilter'],
    });
    expect(generated?.argv).toEqual([
      'kci-dev',
      'results',
      'builds',
      '--origin',
      'maestro',
      '--commit',
      'abc123',
    ]);
    expect(generated?.omittedFilters).toEqual(['tableFilter']);
  });

  it('does not create commands with missing required values', () => {
    expect(createTreeListingCommand({ origin: 'maestro' })).toBeUndefined();
    expect(
      createTreeResultsCommand('builds', { origin: 'maestro' }),
    ).toBeUndefined();
    expect(createResultDetailsCommand('build')).toBeUndefined();
    expect(createHardwareListingCommand({})).toBeUndefined();
    expect(
      createHardwareResultsCommand('builds', { origin: 'maestro' }),
    ).toBeUndefined();
  });

  it('quotes unsafe and empty shell arguments', () => {
    expect(
      serializeShellArgv([
        'plain',
        'two words',
        "it's",
        'stop; now',
        '$(touch /tmp/no)',
        'line\nbreak',
        '',
      ]),
    ).toBe(
      `plain 'two words' 'it'"'"'s' 'stop; now' '$(touch /tmp/no)' 'line\nbreak' ''`,
    );
  });

  it('does not add JSON or log-download flags by default', () => {
    const commands = [
      createResultDetailsCommand('test', 'id'),
      createHardwareListingCommand({ origin: 'maestro' }),
      createHardwareResultsCommand('tests', {
        name: 'qemu',
        origin: 'maestro',
      }),
    ];
    for (const generated of commands) {
      expect(generated?.argv).not.toContain('--json');
      expect(generated?.argv).not.toContain('--download-logs');
    }
  });

  it('maps only effective tree-build filters and discloses build duration', () => {
    const generated = createTreeResultsCommand('builds', {
      origin: 'maestro',
      commit: 'abc123',
      filters: {
        architectures: ['arm64'],
        configs: ['defconfig'],
        compilers: ['gcc-14'],
        minDuration: 0,
        maxDuration: 20,
      },
    })!;
    expect(generated.argv).toContain('--arch');
    expect(generated.argv).not.toContain('--min-duration');
    expect(generated.omittedFilters).toEqual(['build duration']);
  });

  it('emits boot origin only for tree boots', () => {
    const filters = { bootOrigins: ['tuxsuite'] };
    const treeBoots = createTreeResultsCommand('boots', {
      origin: 'maestro',
      commit: 'abc123',
      filters,
    })!;
    const treeTests = createTreeResultsCommand('tests', {
      origin: 'maestro',
      commit: 'abc123',
      filters,
    })!;
    const hardwareBoots = createHardwareResultsCommand('boots', {
      name: 'qemu',
      origin: 'maestro',
      filters,
    })!;
    expect(treeBoots.argv).toContain('--boot-origin');
    expect(treeTests.argv).not.toContain('--boot-origin');
    expect(treeTests.omittedFilters).toContain('boot origin');
    expect(hardwareBoots.argv).not.toContain('--boot-origin');
  });

  it('discloses hardware architecture and unsupported result origins', () => {
    const generated = createHardwareResultsCommand('tests', {
      name: 'qemu',
      origin: 'checkout-origin',
      filters: {
        architectures: ['arm64'],
        buildOrigins: ['build-origin'],
        testOrigins: ['test-origin'],
      },
    })!;
    expect(generated.argv).not.toContain('--arch');
    expect(generated.omittedFilters).toEqual([
      'architecture',
      'build origin',
      'test origin',
    ]);
  });

  it('extracts build, boot, and test origins independently', () => {
    const state = {
      buildOrigin: { buildA: true },
      bootOrigin: { bootA: true },
      testOrigin: { testA: true },
    } as never;
    expect(dashboardFiltersFromDiffFilter(state, 'tests')).toMatchObject({
      buildOrigins: ['buildA'],
      bootOrigins: ['bootA'],
      testOrigins: ['testA'],
    });
  });

  it('preserves supported numeric zero and shell quoting', () => {
    const generated = createTreeResultsCommand('tests', {
      origin: 'maestro',
      commit: 'two words',
      filters: { minDuration: 0 },
    })!;
    expect(generated.argv).toContain('0');
    expect(serializeShellArgv(generated.argv)).toContain(
      "--commit 'two words'",
    );
  });

  it('omits empty optional filters and rejects whitespace required values', () => {
    const generated = createTreeResultsCommand('tests', {
      origin: 'maestro',
      commit: 'abc',
      branch: '   ',
      filters: { architectures: [''], bootOrigins: ['   '] },
    })!;
    expect(generated.argv).not.toContain('--branch');
    expect(generated.argv).not.toContain('--arch');
    expect(createTreeListingCommand({ origin: ' ', days: 7 })).toBeUndefined();
    expect(createResultDetailsCommand('test', '  ')).toBeUndefined();
    expect(
      createIssueListingCommands({ origins: ['', '  '], days: 5 }),
    ).toEqual([]);
  });

  it('reports active hardware listing restrictions', () => {
    expect(
      createHardwareListingCommand({
        origin: 'maestro',
        filters: {
          hasHardwareDateWindow: true,
          hasTextSearch: true,
          hasTreeSelection: true,
        },
      })?.omittedFilters,
    ).toEqual([
      'hardware date window',
      'client-side text search',
      'tree, branch, and revision selection',
    ]);
  });

  it('creates safe detail variants without downloading by default', () => {
    const generated = createResultDetailsCommand('boot', 'boot-id')!;
    expect(generated.variants).toEqual([
      { id: 'human', label: 'Human-readable', argv: generated.argv },
      { id: 'json', label: 'JSON', argv: [...generated.argv, '--json'] },
      {
        id: 'download',
        label: 'Download logs (writes files)',
        argv: [...generated.argv, '--download-logs'],
        writesFiles: true,
      },
    ]);
    expect(generated.argv).not.toContain('--download-logs');
  });

  it('uses public JSON formats for compare and gate variants', () => {
    const generated = createTreeCompareCommand({
      origin: 'maestro',
      gitUrl: 'https://example.com/linux.git',
      branch: 'main',
      hashA: 'base',
      hashB: 'head',
    })!;
    expect(generated.variants?.map(variant => variant.argv)).toContainEqual([
      ...generated.argv,
      '--format',
      'json',
    ]);
    expect(generated.variants?.map(variant => variant.argv)).toContainEqual([
      'kci-dev',
      'results',
      'gate',
      '--origin',
      'maestro',
      '--giturl',
      'https://example.com/linux.git',
      '--branch',
      'main',
      '--base',
      'base',
      '--head',
      'head',
    ]);
  });
});
