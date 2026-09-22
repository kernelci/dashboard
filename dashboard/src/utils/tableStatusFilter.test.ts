import { describe, expect, it } from 'vitest';

import {
  defaultTableStatusSelection,
  normalizeTableStatusSelection,
  toggleTableStatus,
} from './tableStatusFilter';

describe('toggleTableStatus', () => {
  it('allows an empty selection', () => {
    expect(toggleTableStatus(['failed'], 'failed')).toStrictEqual([]);
  });

  it('uses all statuses when no selection exists', () => {
    expect(toggleTableStatus(undefined, 'failed')).toStrictEqual([
      'success',
      'inconclusive',
    ]);
  });
});

describe('normalizeTableStatusSelection', () => {
  it('preserves empty selections and accepts legacy values', () => {
    expect(normalizeTableStatusSelection([])).toStrictEqual([]);
    expect(normalizeTableStatusSelection('failed')).toStrictEqual(['failed']);
    expect(normalizeTableStatusSelection('all')).toStrictEqual(
      defaultTableStatusSelection,
    );
  });

  it('falls back to default when an array has values but none are valid', () => {
    expect(normalizeTableStatusSelection(['nope'])).toStrictEqual(
      defaultTableStatusSelection,
    );
  });
});
