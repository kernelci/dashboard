import type { Status } from '@/types/database';
import type { StatusCount, BuildStatus } from '@/types/general';

type StatusGroups = 'success' | 'failed' | 'inconclusive';

type GroupStatusCount = {
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

export function groupStatus(counts: GroupStatusCount): GroupedStatus {
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

type FlexibleStatus = BuildStatus | GroupStatusCount | StatusCount;

export function sumStatus(status: FlexibleStatus): number {
  return Object.values(status).reduce(
    (accumulator: number, current) => accumulator + (current ?? 0),
    0,
  );
}
