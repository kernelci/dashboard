import { describe, expect, it } from 'vitest';

import {
  deriveCompareChange,
  applyStatusPairFilter,
  mapBootOrTestDiffRows,
  mapBuildDiffRows,
  normalizeStatusPairs,
  parseStatusPairs,
  resolveStatusPairs,
  serializeStatusPairs,
  toggleChangeTypePairs,
} from './treeCompareDiff';

describe('deriveCompareChange', () => {
  it('maps backend change-count transitions', () => {
    expect(deriveCompareChange('PASS', 'FAIL')).toBe('regression');
    expect(deriveCompareChange('FAIL', 'PASS')).toBe('fixed');
    expect(deriveCompareChange('—', 'FAIL')).toBe('newFailure');
    expect(deriveCompareChange('FAIL', 'FAIL')).toBe('stillFailing');
    expect(deriveCompareChange('—', 'PASS')).toBe('newPass');
  });

  it('classifies one-sided presence as appeared/disappeared', () => {
    expect(deriveCompareChange('—', 'INCONCLUSIVE')).toBe('appeared');
    expect(deriveCompareChange('PASS', '—')).toBe('disappeared');
    expect(deriveCompareChange('FAIL', '—')).toBe('disappeared');
    expect(deriveCompareChange('INCONCLUSIVE', '—')).toBe('disappeared');
  });

  it('classifies INCONCLUSIVE transitions like the backend counts', () => {
    expect(deriveCompareChange('PASS', 'INCONCLUSIVE')).toBe('regression');
    expect(deriveCompareChange('FAIL', 'INCONCLUSIVE')).toBe('fixed');
    expect(deriveCompareChange('INCONCLUSIVE', 'FAIL')).toBe('newFailure');
    expect(deriveCompareChange('INCONCLUSIVE', 'PASS')).toBe('newPass');
  });
});

describe('applyStatusPairFilter', () => {
  const rows = [
    { id: '1', sideA: 'PASS' as const, sideB: 'FAIL' as const },
    { id: '2', sideA: 'FAIL' as const, sideB: 'PASS' as const },
    { id: '3', sideA: 'FAIL' as const, sideB: 'FAIL' as const },
    { id: '4', sideA: '—' as const, sideB: 'FAIL' as const },
  ];

  it('keeps rows matching any selected pair', () => {
    expect(
      applyStatusPairFilter(rows, [
        { from: 'PASS', to: 'FAIL' },
        { from: 'FAIL', to: 'PASS' },
      ]).map(row => row.id),
    ).toEqual(['1', '2']);
  });

  it('returns all rows when nothing is selected', () => {
    expect(applyStatusPairFilter(rows, [])).toEqual(rows);
  });
});

describe('parse/normalize/serialize status pairs', () => {
  it('round-trips pairs including absent', () => {
    expect(parseStatusPairs(['PASS:FAIL', 'ABSENT:FAIL'])).toEqual([
      { from: 'PASS', to: 'FAIL' },
      { from: '—', to: 'FAIL' },
    ]);
    expect(
      serializeStatusPairs([
        { from: 'PASS', to: 'FAIL' },
        { from: '—', to: 'FAIL' },
      ]),
    ).toEqual(['PASS:FAIL', 'ABSENT:FAIL']);
  });

  it('uses none for an empty list and parses it back to empty', () => {
    expect(serializeStatusPairs([])).toEqual(['none']);
    expect(parseStatusPairs(['none'])).toEqual([]);
    expect(parseStatusPairs([])).toEqual([]);
  });

  it('drops invalid and duplicate pairs', () => {
    expect(
      parseStatusPairs(['PASS:FAIL', 'NOPE:FAIL', 'PASS:FAIL', 'FAIL:PASS']),
    ).toEqual([
      { from: 'PASS', to: 'FAIL' },
      { from: 'FAIL', to: 'PASS' },
    ]);
    expect(
      normalizeStatusPairs([
        { from: 'PASS', to: 'FAIL' },
        { from: 'PASS', to: 'FAIL' },
      ]),
    ).toEqual([{ from: 'PASS', to: 'FAIL' }]);
  });
});

describe('resolveStatusPairs', () => {
  const stored = ['ABSENT:FAIL'];
  const url = ['PASS:FAIL', 'FAIL:PASS'];

  it('uses URL pairs when present, ignoring storage', () => {
    expect(resolveStatusPairs(url, stored)).toEqual([
      { from: 'PASS', to: 'FAIL' },
      { from: 'FAIL', to: 'PASS' },
    ]);
  });

  it('treats none in the URL as an empty list, ignoring storage', () => {
    expect(resolveStatusPairs(['none'], stored)).toEqual([]);
  });

  it('uses storage when the URL omits statusPair', () => {
    expect(resolveStatusPairs(undefined, stored)).toEqual([
      { from: '—', to: 'FAIL' },
    ]);
  });

  it('uses the hardcoded default when URL and storage are both missing', () => {
    expect(resolveStatusPairs(undefined, undefined)).toEqual([
      { from: 'PASS', to: 'FAIL' },
      { from: 'FAIL', to: 'PASS' },
    ]);
  });
});

describe('toggleChangeTypePairs', () => {
  it('adds every pair for a change type', () => {
    expect(toggleChangeTypePairs([], 'regression')).toEqual([
      { from: 'PASS', to: 'FAIL' },
      { from: 'PASS', to: 'INCONCLUSIVE' },
    ]);
  });

  it('removes those pairs when the chip is already complete', () => {
    expect(
      toggleChangeTypePairs(
        [
          { from: 'PASS', to: 'FAIL' },
          { from: 'PASS', to: 'INCONCLUSIVE' },
          { from: 'FAIL', to: 'PASS' },
        ],
        'regression',
      ),
    ).toEqual([{ from: 'FAIL', to: 'PASS' }]);
  });

  it('completes a partial chip instead of removing it', () => {
    expect(
      toggleChangeTypePairs([{ from: 'PASS', to: 'FAIL' }], 'regression'),
    ).toEqual([
      { from: 'PASS', to: 'FAIL' },
      { from: 'PASS', to: 'INCONCLUSIVE' },
    ]);
  });
});

describe('mapBuildDiffRows', () => {
  it('maps snake_case API rows into table rows', () => {
    const [row] = mapBuildDiffRows([
      {
        config_name: 'defconfig',
        architecture: 'arm64',
        compiler: 'gcc',
        status_a: 'PASS',
        status_b: 'FAIL',
      },
    ]);

    expect(row).toMatchObject({
      config: 'defconfig',
      arch: 'arm64',
      compiler: 'gcc',
      sideA: 'PASS',
      sideB: 'FAIL',
      change: 'regression',
    });
  });
});

describe('mapBootOrTestDiffRows', () => {
  it('maps platform to hardware and null status to dash', () => {
    const [row] = mapBootOrTestDiffRows(
      [
        {
          path: 'boot',
          config_name: 'defconfig',
          architecture: 'arm64',
          platform: 'qemu-arm64',
          status_a: null,
          status_b: 'FAIL',
        },
      ],
      'boot',
    );

    expect(row).toMatchObject({
      path: 'boot',
      config: 'defconfig',
      arch: 'arm64',
      hardware: 'qemu-arm64',
      sideA: '—',
      sideB: 'FAIL',
      change: 'newFailure',
    });
  });
});
