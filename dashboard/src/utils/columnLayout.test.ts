/* eslint-disable no-magic-numbers */
import { describe, expect, it } from 'vitest';

import {
  distributeWidths,
  ensureRowHeadersFirst,
  getColumnId,
  moveColumnInOrder,
  normalizeColumns,
  resizeAdjacentColumns,
  resizeOuterColumn,
} from './columnLayout';

describe('distributeWidths', () => {
  const cols = [
    { id: 'a', minWidth: 100, maxWidth: 200, widthWeight: 1 },
    { id: 'b', minWidth: 100, maxWidth: 200, widthWeight: 1 },
  ];

  it('uses maxWidth when remaining space is abundant', () => {
    const widths = distributeWidths(500, cols, {});
    expect(widths).toEqual({ a: 200, b: 200 });
  });

  it('uses minWidth and allows overflow when space is tight', () => {
    const widths = distributeWidths(150, cols, {});
    expect(widths).toEqual({ a: 100, b: 100 });
  });

  it('splits remaining space by widthWeight between min and max', () => {
    const widths = distributeWidths(300, cols, {});
    expect(widths).toEqual({ a: 150, b: 150 });
  });

  it('respects widthWeight ratios', () => {
    const weighted = [
      { id: 'a', minWidth: 50, maxWidth: 400, widthWeight: 1 },
      { id: 'b', minWidth: 50, maxWidth: 400, widthWeight: 3 },
    ];
    const widths = distributeWidths(400, weighted, {});
    expect(widths).toEqual({ a: 100, b: 300 });
  });

  it('keeps manual columnSizing fixed and distributes the rest', () => {
    const three = [
      { id: 'a', minWidth: 50, maxWidth: 200, widthWeight: 1 },
      { id: 'b', minWidth: 50, maxWidth: 200, widthWeight: 1 },
      { id: 'c', minWidth: 50, maxWidth: 200, widthWeight: 1 },
    ];
    const widths = distributeWidths(400, three, { a: 120 });
    expect(widths.a).toBe(120);
    expect(widths.b).toBe(140);
    expect(widths.c).toBe(140);
  });
});

describe('ensureRowHeadersFirst', () => {
  it('moves row header ids to the front in header order', () => {
    expect(ensureRowHeadersFirst(['b', 'a', 'c'], ['a', 'b'])).toEqual([
      'a',
      'b',
      'c',
    ]);
  });
});

describe('moveColumnInOrder', () => {
  it('reorders non-header columns only', () => {
    expect(moveColumnInOrder(['h', 'a', 'b'], 'a', 1, ['h'])).toEqual([
      'h',
      'b',
      'a',
    ]);
  });

  it('does not move row header columns', () => {
    expect(moveColumnInOrder(['h', 'a'], 'h', 1, ['h'])).toEqual(['h', 'a']);
  });
});

describe('getColumnId', () => {
  it('matches TanStack id derivation for dotted accessorKeys', () => {
    expect(getColumnId({ accessorKey: 'build_status.PASS' })).toBe(
      'build_status_PASS',
    );
  });

  it('prefers an explicit id', () => {
    expect(
      getColumnId({ id: 'build_status', accessorKey: 'build_status.PASS' }),
    ).toBe('build_status');
  });
});

describe('normalizeColumns', () => {
  it('sets enableHiding false for isRowHeader and maps width meta', () => {
    const [column] = normalizeColumns(
      [
        {
          accessorKey: 'tree_name',
          meta: { isRowHeader: true, minWidth: 120, maxWidth: 240 },
        },
      ],
      { minWidth: 80, maxWidth: 320 },
    );

    expect(column.enableHiding).toBe(false);
    expect(column.minSize).toBe(120);
    expect(column.maxSize).toBe(240);
    expect(column.meta).toMatchObject({
      isRowHeader: true,
      minWidth: 120,
      maxWidth: 240,
      widthWeight: 1,
    });
  });
});

describe('resizeAdjacentColumns', () => {
  it('moves width between columns while keeping the total fixed', () => {
    expect(
      resizeAdjacentColumns(
        { startWidth: 100, minWidth: 40 },
        { startWidth: 100, minWidth: 40 },
        30,
      ),
    ).toEqual({ leftWidth: 130, rightWidth: 70 });
  });

  it('stops when the right column hits minWidth', () => {
    expect(
      resizeAdjacentColumns(
        { startWidth: 100, minWidth: 40 },
        { startWidth: 100, minWidth: 80 },
        50,
      ),
    ).toEqual({ leftWidth: 120, rightWidth: 80 });
  });

  it('stops when the left column hits minWidth', () => {
    expect(
      resizeAdjacentColumns(
        { startWidth: 100, minWidth: 80 },
        { startWidth: 100, minWidth: 40 },
        -50,
      ),
    ).toEqual({ leftWidth: 80, rightWidth: 120 });
  });

  it('does not clamp to a max width', () => {
    expect(
      resizeAdjacentColumns(
        { startWidth: 100, minWidth: 40 },
        { startWidth: 400, minWidth: 40 },
        250,
      ),
    ).toEqual({ leftWidth: 350, rightWidth: 150 });
  });
});

describe('resizeOuterColumn', () => {
  it('grows without a max clamp and respects minWidth', () => {
    expect(resizeOuterColumn(100, 40, 500)).toBe(600);
    expect(resizeOuterColumn(100, 80, -50)).toBe(80);
  });
});
