import type { Status } from '@/types/database';
import type {
  StatusCount,
  BuildStatus,
  RequiredStatusCount,
} from '@/types/general';

type StatusGroups = 'success' | 'failed' | 'inconclusive';

type GroupStatusCount = {
  doneCount?: number;
  missCount?: number;
  skipCount?: number;
  errorCount?: number;
  failCount?: number;
  passCount?: number;
  nullCount?: number;
};

type GroupedStatus = {
  successCount: number;
  inconclusiveCount: number;
  failedCount: number;
};

export function groupStatus(counts: GroupStatusCount): GroupedStatus {
  return {
    successCount: counts.passCount ?? 0,
    failedCount: counts.failCount ?? 0,
    inconclusiveCount:
      (counts.doneCount ?? 0) +
      (counts.errorCount ?? 0) +
      (counts.missCount ?? 0) +
      (counts.skipCount ?? 0) +
      (counts.nullCount ?? 0),
  };
}

export const getStatusGroup = (status: Status): StatusGroups => {
  if (status === 'PASS') {
    return 'success';
  }
  if (status === 'FAIL') {
    return 'failed';
  }
  return 'inconclusive';
};

type FlexibleStatus = BuildStatus | GroupStatusCount | StatusCount;

export function sumStatus(status: FlexibleStatus): number {
  return Object.values(status).reduce(
    (accumulator: number, current) => accumulator + (current ?? 0),
    0,
  );
}

export const statusCountToRequiredStatusCount = (
  statusCount: StatusCount,
): RequiredStatusCount => {
  return {
    PASS: statusCount.PASS ?? 0,
    FAIL: statusCount.FAIL ?? 0,
    MISS: statusCount.MISS ?? 0,
    SKIP: statusCount.SKIP ?? 0,
    ERROR: statusCount.ERROR ?? 0,
    NULL: statusCount.NULL ?? 0,
    DONE: statusCount.DONE ?? 0,
  };
};
