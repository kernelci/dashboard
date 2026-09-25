import { describe, expect, it } from 'vitest';

import { getActiveDurationFilter, zDiffFilter } from '@/types/general';
import { mapFilterToReq } from '@/components/Tabs/Filters';
import { createFlatFilter } from '@/components/Tabs/FilterList';
import { cleanFalseFilters } from '@/components/Tabs/tabsUtils';
import { parseSearch } from '@/utils/search';

describe('getActiveDurationFilter', () => {
  const durationSeconds = 42;

  it('rejects zero, NaN, blank strings, and non-numeric values', () => {
    expect(getActiveDurationFilter(0)).toBeUndefined();
    expect(getActiveDurationFilter(Number.NaN)).toBeUndefined();
    expect(getActiveDurationFilter('')).toBeUndefined();
    expect(getActiveDurationFilter('   ')).toBeUndefined();
    expect(getActiveDurationFilter(undefined)).toBeUndefined();
    expect(getActiveDurationFilter(null)).toBeUndefined();
    expect(getActiveDurationFilter(true)).toBeUndefined();
    expect(getActiveDurationFilter([durationSeconds])).toBeUndefined();
    expect(getActiveDurationFilter({})).toBeUndefined();
  });

  it('accepts numbers and numeric strings', () => {
    expect(getActiveDurationFilter(durationSeconds)).toBe(durationSeconds);
    expect(getActiveDurationFilter(String(durationSeconds))).toBe(
      durationSeconds,
    );
  });
});

describe('zero duration is not an active filter', () => {
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

  it('mapFilterToReq does not send zero duration to the API', () => {
    const mapped = mapFilterToReq(durationZeroFilter) as Record<
      string,
      string[]
    >;
    expect(mapped['treeDetails.config_name']).toEqual(['arm64']);
    expect(mapped['treeDetails.duration_[gte]']).toBeUndefined();
  });

  it('keeps non-zero duration across apply, chips, and API mapping', () => {
    const filter = { buildDurationMin: 42, bootDurationMax: 60 };

    expect(cleanFalseFilters(filter)).toEqual(filter);
    expect(createFlatFilter(filter)).toEqual([
      'buildDurationMin:42',
      'bootDurationMax:60',
    ]);
    expect(mapFilterToReq(filter) as Record<string, string[]>).toMatchObject({
      'treeDetails.duration_[gte]': ['42'],
      'boot.duration_[lte]': ['60'],
    });
  });

  it('round-trips duration in the URL with chips and API mapping', () => {
    const buildDurationMin = 42;
    const parsed = parseSearch(`df|bdf=${buildDurationMin}&df|c|arm=true`) as {
      diffFilter: Record<string, unknown>;
    };

    expect(parsed.diffFilter.buildDurationMin).toBe(buildDurationMin);
    expect(zDiffFilter.parse(parsed.diffFilter)).toEqual({
      buildDurationMin,
      configs: { arm: true },
    });
    expect(createFlatFilter(zDiffFilter.parse(parsed.diffFilter))).toEqual([
      'configs:arm',
      `buildDurationMin:${buildDurationMin}`,
    ]);
  });
});
