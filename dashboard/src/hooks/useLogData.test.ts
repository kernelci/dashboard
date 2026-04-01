import { describe, expect, it } from 'vitest';

import { processLogData } from './useLogData';

describe('processLogData', () => {
  it('maps build fields and defaults status to NULL when missing', () => {
    const result = processLogData('build-1', {
      type: 'build',
      git_commit_name: 'Fix scheduler race',
      misc: { platform: 'qemu-x86' },
      output_files: [{ name: 'other_file', url: 'https://example.com/other' }],
    });

    expect(result).toMatchObject({
      id: 'build-1',
      type: 'build',
      title: 'Fix scheduler race',
      status: 'NULL',
      hardware: 'qemu-x86',
      log_excerpt: undefined,
    });
  });

  it('maps test fields and picks first hardware candidate from buildHardwareArray', () => {
    const result = processLogData('test-1', {
      type: 'test',
      path: 'boot/smoke',
      status: 'PASS',
      environment_misc: { platform: 'rk3399' },
      environment_compatible: ['arm64', 'lab-board'],
    });

    expect(result).toMatchObject({
      id: 'test-1',
      type: 'test',
      title: 'boot/smoke',
      status: 'PASS',
      hardware: 'rk3399',
    });
  });

  it('extracts log excerpt URL from output_files when present', () => {
    const result = processLogData('build-2', {
      type: 'build',
      status: 'FAIL',
      output_files: [
        { name: 'artifact', url: 'https://example.com/artifact' },
        { name: 'log_excerpt', url: 'https://example.com/log-excerpt' },
      ],
    });

    expect(result.log_excerpt).toBe('https://example.com/log-excerpt');
  });
});
