import type { UseQueryResult } from '@tanstack/react-query';

import { useBuildDetails } from '@/api/buildDetails';
import { useTestDetails } from '@/api/testDetails';
import type { Status } from '@/types/database';
import type { TBuildDetails } from '@/types/tree/BuildDetails';
import type { TTestDetails } from '@/types/tree/TestDetails';
import { buildHardwareArray } from '@/utils/table';

export interface LogData {
  id: string;
  type: LogType;
  title?: string;
  status?: Status;
  git_commit_hash?: string;
  git_repository_branch?: string;
  git_repository_url?: string;
  tree_name?: string;
  hardware?: string;
  architecture?: string;
  log_url?: string;
  log_excerpt?: string;
}

export type LogType = 'build' | 'test';
type FullLogQuery<T extends TBuildDetails | TTestDetails> = Omit<
  UseQueryResult<T>,
  'data'
> & {
  data: LogData;
};

type TypedTBuildDetails = Partial<TBuildDetails> & {
  type: 'build';
};

type TypedTTestDetails = Partial<TTestDetails> & {
  type: 'test';
};

export const processLogData = (
  id: string,
  data: TypedTBuildDetails | TypedTTestDetails,
): LogData => {
  const handledStatus = data?.status ?? 'NULL';
  const handledTitle =
    data?.type === 'build' ? data.git_commit_name : data?.path;
  const handledHardware: string | undefined =
    data.type === 'test'
      ? buildHardwareArray(
          data?.environment_compatible,
          data?.environment_misc,
        )?.[0]
      : typeof data?.misc?.platform === 'string'
        ? data.misc.platform
        : undefined;

  return {
    id,
    type: data.type,
    title: handledTitle,
    tree_name: data?.tree_name,
    git_commit_hash: data?.git_commit_hash,
    git_repository_branch: data?.git_repository_branch,
    git_repository_url: data?.git_repository_url,
    architecture: data?.architecture,
    log_url: data?.log_url,
    log_excerpt: data?.log_excerpt,
    status: handledStatus,
    hardware: handledHardware,
  };
};

export const useLogData = (
  id: string,
  type?: LogType,
): FullLogQuery<TBuildDetails | TTestDetails> => {
  const buildQuery = useBuildDetails(id, {
    enabled: type === 'build' && id !== '',
  });
  const testQuery = useTestDetails(id, {
    enabled: type === 'test' && id !== '',
  });
  const activeQuery = type === 'build' ? buildQuery : testQuery;
  const data: TypedTBuildDetails | TypedTTestDetails =
    type === 'build'
      ? ({ ...buildQuery.data, type: 'build' } as TypedTBuildDetails)
      : ({ ...testQuery.data, type: 'test' } as TypedTTestDetails);
  const logData = processLogData(id, data);

  return {
    ...activeQuery,
    data: logData,
  };
};
