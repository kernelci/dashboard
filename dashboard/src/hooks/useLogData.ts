import { useMemo } from 'react';

import { useBuildDetails } from '@/api/buildDetails';
import { useTestDetails } from '@/api/testDetails';
import type { Status } from '@/types/database';
import type { TBuildDetails } from '@/types/tree/BuildDetails';

interface LogData {
  status?: Status;
  git_commit_hash?: string;
  git_repository_branch?: string;
  git_repository_url?: string;
  log_url?: string;
  log_excerpt?: string;
  id: string;
}

export type LogType = 'build' | 'test';

export function useLogData(id: string, type: LogType) {
  // TODO add enabled for queries
  const buildQuery = useBuildDetails(id, { enabled: type === 'build' });
  const testQuery = useTestDetails(id, { enabled: type === 'test' });

  const activeQuery = type === 'build' ? buildQuery : testQuery;
  const data = activeQuery.data;

  const handledStatus: Status = useMemo(() => {
    if (type === 'build') {
      return buildQuery.data?.valid ? 'PASS' : 'FAIL';
    } else {
      return testQuery?.data?.status ?? 'NULL';
    }
  }, [buildQuery.data?.valid, testQuery?.data?.status, type]);

  const logData: LogData = {
    id,
    git_commit_hash: data?.git_commit_hash,
    git_repository_branch: data?.git_repository_branch,
    git_repository_url: data?.git_repository_url,
    log_url: data?.log_url,
    log_excerpt: data?.log_excerpt,
    status: handledStatus,
  };

  return {
    ...activeQuery,
    data: logData,
  };
}
