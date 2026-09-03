import { describe, expect, it } from 'vitest';

import { daysToSeconds } from '@/utils/date';

import {
  createHardwareListingCommand,
  createHardwareResultsCommand,
  createIssueDetailsCommand,
  createIssueListingCommands,
  createIssueListingCommandsFromState,
  createResultDetailsCommand,
  createTreeCompareCommand,
  createTreeListingCommand,
  createTreeResultsCommand,
  serializeKcidevCommand,
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
      expect(serializeKcidevCommand(generated!)).not.toContain('--git-url');
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
    ).toEqual([
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
});
