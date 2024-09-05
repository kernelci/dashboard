import { z } from 'zod';

export type TreeTableBody = {
  commitHash: string;
  commitName: string;
  patchsetHash: string;
  buildStatus: {
    valid: number;
    invalid: number;
    null: number;
  };
  tree_names: string[];
  testStatus: {
    done: number;
    pass: number;
    error: number;
    fail: number;
    skip: number;
    miss: number;
  };
  bootStatus: {
    done: number;
    pass: number;
    error: number;
    fail: number;
    skip: number;
    miss: number;
  };
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
  git_commit_name: string | null;
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
  boot_status: {
    done: number;
    pass: number;
    error: number;
    fail: number;
    skip: number;
    miss: number;
  };
};

const origins = [
  '0dayci',
  'broonie',
  'maestro',
  'microsoft',
  'redhat',
  'syzbot',
  'tuxsuite',
] as const;
const DEFAULT_ORIGIN = 'maestro';

export const zOriginEnum = z.enum(origins);
export const zOrigin = zOriginEnum.catch(DEFAULT_ORIGIN);
