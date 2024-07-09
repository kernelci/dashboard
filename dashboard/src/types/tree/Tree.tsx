export type TreeTableBody = {
  name: string;
  branch: string;
  commit: string;
  buildStatus: string;
  testStatus: string;
};

export type Tree = {
  tree_name: string | null;
  git_commit_hash: string | null;
  git_commit_name: string | null;
  git_repository_branch: string | null;
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
