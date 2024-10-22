import type { InconclusiveStatus } from '@/types/database';

export const status = [
  'MISS',
  'ERROR',
  'FAIL',
  'PASS',
  'SKIP',
  'DONE',
  'NULL',
] as const;

export const StatusTable = {
  MISS: 'MISS',
  ERROR: 'ERROR',
  FAIL: 'FAIL',
  PASS: 'PASS',
  SKIP: 'SKIP',
  DONE: 'DONE',
} as const;

const inconclusiveStatus = [
  'ERROR',
  'SKIP',
  'DONE',
  'MISS',
] as const satisfies InconclusiveStatus[];

export const errorStatusSet = new Set(inconclusiveStatus);
