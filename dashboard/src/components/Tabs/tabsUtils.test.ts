import { describe, expect, it } from 'vitest';

import { getActiveDurationFilter } from '@/types/general';
import { createFlatFilter } from '@/components/Tabs/FilterList';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';

describe('getActiveDurationFilter', () => {
  it('rejects zero, NaN, and undefined', () => {
    expect(getActiveDurationFilter(0)).toBeUndefined();
    expect(getActiveDurationFilter(Number.NaN)).toBeUndefined();
    expect(getActiveDurationFilter(undefined)).toBeUndefined();
  });

  it('accepts positive numbers', () => {
    const durationSeconds = 30;
    expect(getActiveDurationFilter(durationSeconds)).toBe(durationSeconds);
  });
});

describe('duration filter issue #428', () => {
  const durationZeroFilter = {
    buildDurationMin: 0,
    configs: { arm64: true },
  };

  it('cleanFalseFilters drops zero duration before persisting to URL', () => {
    expect(cleanFalseFilters(durationZeroFilter)).toEqual({
      configs: { arm64: true },
    });
  });

  it('createFlatFilter does not show a chip for zero duration', () => {
    expect(createFlatFilter(durationZeroFilter)).toEqual(['configs:arm64']);
  });

  it('keeps non-zero duration across apply and chips', () => {
    const filter = { buildDurationMin: 120, bootDurationMax: 60 };

    expect(cleanFalseFilters(filter)).toEqual(filter);
    expect(createFlatFilter(filter)).toEqual([
      'buildDurationMin:120',
      'bootDurationMax:60',
    ]);
  });
});
