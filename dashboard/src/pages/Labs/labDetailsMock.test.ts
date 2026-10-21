import { describe, expect, it } from 'vitest';

import {
  aggregateLabTrees,
  dailyStatus,
  FILL_GREEN_AT,
  FILL_YELLOW_AT,
  fillCount,
  fillTone,
  frequencySlices,
  labAttentionItems,
  labDetailsMock,
  sumStatusCounts,
  toTestHistory,
} from './labDetailsMock';

describe('labDetailsMock', () => {
  it('keeps card totals equal to the sample rows', () => {
    const trees = labDetailsMock('lab-baylibre');
    const passRows = trees.reduce(
      (total, tree) =>
        total + tree.buildRows.filter(row => row.status === 'PASS').length,
      0,
    );

    expect(sumStatusCounts(trees.map(tree => tree.builds)).PASS).toBe(passRows);
    expect(trees[0]?.bootRows[0]?.platform).toBe('meson-g12b-odroid-n2');
    expect(aggregateLabTrees(trees.slice(0, 1)).buildRows).toHaveLength(
      trees[0]?.buildRows.length ?? 0,
    );
    const days = trees[0]?.buildRows.length ?? 0;
    const counts = dailyStatus('builds', days, trees.length);
    expect(days).toBeGreaterThan(0);
    expect(counts.pass).toHaveLength(days);
    expect(counts.fail).toHaveLength(days);
    expect(counts.inconclusive).toHaveLength(days);
    expect(
      Math.max(...counts.pass) - Math.min(...counts.pass),
    ).toBeLessThanOrEqual(trees.length);
    const history = toTestHistory(trees[0]?.testRows ?? [], 'lab-baylibre');
    expect(history).toHaveLength(trees[0]?.testRows.length ?? 0);
    expect(history[0]?.path).toBe(trees[0]?.testRows[0]?.path);
    expect(history[0]?.lab).toBe('lab-baylibre');
    expect(Number.isNaN(Date.parse(history[0]?.start_time ?? ''))).toBe(false);
  });

  it('keeps unknown out of the named slices and folds the tail into other', () => {
    const slices = frequencySlices(['a', 'a', 'a', 'b', 'b', 'c', '  '], 2);

    expect(slices).toEqual([
      { name: 'a', value: 3, kind: 'named' },
      { name: 'b', value: 2, kind: 'named' },
      { name: '', value: 1, kind: 'other' },
      { name: '', value: 1, kind: 'unknown' },
    ]);
    expect(fillCount([true, false, true])).toEqual({ filled: 2, total: 3 });
    expect(fillTone(FILL_GREEN_AT)).toBe('good');
    expect(fillTone(FILL_YELLOW_AT)).toBe('mid');
    expect(fillTone(FILL_YELLOW_AT - 1)).toBe('bad');
  });

  it('shows the boot and kselftest failures on the same lab page', () => {
    const items = labAttentionItems('lava-broonie');

    expect(items.map(item => item.test)).toEqual(['boot', 'kselftest']);
    expect(labAttentionItems('pull-labs-demo')).toBe(items);
    expect(labAttentionItems('lab-baylibre')).toEqual([]);
  });
});
