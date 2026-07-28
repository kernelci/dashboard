import { describe, expect, it } from 'vitest';

import type { SortingState } from '@tanstack/react-table';

import { TABLE_SORT_UNSORTED } from '@/types/general';

import {
  getTableSortValue,
  searchValueToSorting,
  sortingToSearchValue,
  updateTableSortParam,
} from './useSortingState';

describe('sortingToSearchValue', () => {
  it('encodes unsorted as none', () => {
    expect(sortingToSearchValue([])).toBe(TABLE_SORT_UNSORTED);
  });

  it('encodes ascending and descending sorts', () => {
    expect(sortingToSearchValue([{ id: 'status', desc: false }])).toBe(
      'status',
    );
    expect(sortingToSearchValue([{ id: 'status', desc: true }])).toBe(
      '-status',
    );
  });
});

describe('searchValueToSorting', () => {
  const defaultSorting: SortingState = [{ id: 'first_seen', desc: true }];

  it('returns default when value is absent', () => {
    expect(searchValueToSorting(undefined, defaultSorting)).toEqual(
      defaultSorting,
    );
  });

  it('parses none as unsorted', () => {
    expect(searchValueToSorting(TABLE_SORT_UNSORTED, defaultSorting)).toEqual(
      [],
    );
  });

  it('parses ascending and descending values', () => {
    expect(searchValueToSorting('status', [])).toEqual([
      { id: 'status', desc: false },
    ]);
    expect(searchValueToSorting('-status', [])).toEqual([
      { id: 'status', desc: true },
    ]);
  });
});

describe('getTableSortValue', () => {
  it('reads a flat string when no sortKey is set', () => {
    expect(getTableSortValue('-status')).toBe('-status');
    expect(getTableSortValue({ buildsTable: 'path' })).toBeUndefined();
  });

  it('reads a keyed value when sortKey is set', () => {
    expect(getTableSortValue({ buildsTable: 'path' }, 'buildsTable')).toBe(
      'path',
    );
    expect(getTableSortValue('-status', 'buildsTable')).toBeUndefined();
  });
});

describe('updateTableSortParam', () => {
  it('stores a flat string without a sortKey', () => {
    expect(updateTableSortParam(undefined, undefined, '-status')).toBe(
      '-status',
    );
    expect(updateTableSortParam('-status', undefined, undefined)).toBe(
      undefined,
    );
  });

  it('stores keyed values when sortKey is set', () => {
    expect(updateTableSortParam(undefined, 'buildsTable', 'path')).toEqual({
      buildsTable: 'path',
    });
    expect(
      updateTableSortParam({ buildsTable: 'path' }, 'testsTable', '-startTime'),
    ).toEqual({
      buildsTable: 'path',
      testsTable: '-startTime',
    });
    expect(
      updateTableSortParam({ buildsTable: 'path' }, 'buildsTable', undefined),
    ).toBeUndefined();
  });
});
