import { describe, expect, it } from 'vitest';

import {
  createHardwareListingCommand,
  createHardwareResultsCommand,
  createResultDetailsCommand,
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
