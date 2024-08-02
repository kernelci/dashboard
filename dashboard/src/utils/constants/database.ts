import type { ErrorStatus } from '@/types/database';

export const status = [
  'MISS',
  'ERROR',
  'FAIL',
  'PASS',
  'SKIP',
  'DONE',
] as const;

const errorStatus = ['MISS', 'ERROR', 'FAIL'] as const satisfies ErrorStatus[];

export const errorStatusSet = new Set(errorStatus);
