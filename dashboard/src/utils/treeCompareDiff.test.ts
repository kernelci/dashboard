import { describe, expect, it } from 'vitest';

import {
  deriveCompareChange,
  applyChangeFilter,
  mapBootOrTestDiffRows,
  mapBuildDiffRows,
  toggleChangeFilter,
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

describe('applyChangeFilter', () => {
  const rows = [
    { id: '1', change: 'regression' as const },
    { id: '2', change: 'fixed' as const },
    { id: '3', change: 'stillFailing' as const },
    { id: '4', change: 'newPass' as const },
  ];

  it('keeps only selected change types', () => {
    expect(
      applyChangeFilter(rows, ['regression', 'fixed']).map(r => r.id),
    ).toEqual(['1', '2']);
  });

  it('returns all rows when nothing is selected', () => {
    expect(applyChangeFilter(rows, [])).toEqual(rows);
  });

  it('returns all rows when every filter chip is selected', () => {
    expect(
      applyChangeFilter(rows, [
        'regression',
        'fixed',
        'newFailure',
        'stillFailing',
        'newPass',
        'appeared',
        'disappeared',
      ]),
    ).toEqual(rows);
  });
});

describe('toggleChangeFilter', () => {
  it('adds and removes values in stable order', () => {
    expect(toggleChangeFilter(['regression'], 'fixed')).toEqual([
      'regression',
      'fixed',
    ]);
    expect(toggleChangeFilter(['regression', 'fixed'], 'regression')).toEqual([
      'fixed',
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
