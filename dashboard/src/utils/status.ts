import { Status } from '@/types/database';

type StatusGroups = 'success' | 'failed' | 'inconclusive';

type StatusCount = {
  doneCount: number;
  missCount: number;
  skipCount: number;
  errorCount: number;
  failCount: number;
  passCount: number;
  nullCount?: number;
};

type GroupedStatus = {
  successCount: number;
  inconclusiveCount: number;
  failedCount: number;
};

export function groupStatus(counts: StatusCount): GroupedStatus {
  return {
    successCount: counts.passCount,
    failedCount: counts.failCount,
    inconclusiveCount:
      counts.doneCount +
      counts.errorCount +
      counts.missCount +
      counts.skipCount +
      (counts.nullCount ?? 0),
  };
}

export const getStatusGroup = (status: Status): StatusGroups => {
  if (status === 'PASS') return 'success';
  if (status === 'FAIL') return 'failed';
  return 'inconclusive';
};
