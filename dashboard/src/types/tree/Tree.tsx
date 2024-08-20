import { z } from 'zod';

export type TreeTableBody = {
  commit: string;
  patchsetHash: string;
  buildStatus: string;
  tree_names: string[];
  testStatus: string;
  id: string;
  branch: string;
  date: string;
  url: string;
};

export type Tree = {
  git_commit_hash: string | null;
  patchset_hash: string | null;
  tree_names: string[];
  git_repository_branch: string | null;
  start_time: string | null;
  git_repository_url: string | null;
  build_status: {
    valid: number;
    invalid: number;
    null: number;
    total: number;
  };
  test_status: {
    fail: number;
    error: number;
    miss: number;
    pass: number;
    done: number;
    skip: number;
    null: number;
    total: number;
  };
};

const origins = [
  '0dayci',
  'broonie',
  'kernelci',
  'maestro',
  'microsoft',
  'redhat',
  'syzbot',
  'tuxsuite',
] as const;

export const zOriginEnum = z.enum(origins);
export const zOrigin = zOriginEnum.catch(origins[0]);
