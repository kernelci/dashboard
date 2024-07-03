export type TreeTableBody = {
    name: string;
    branch: string;
    commit: string;
    buildStatus: string;
    testStatus: string;
}

export type Tree = {
    _timestamp: string;
    id:	string;
    origin:	string | null;
    tree_name: string | null;
    git_repository_url:	string | null;
    git_commit_hash: string | null;
    git_commit_name: string | null;
    git_repository_branch: string | null;
    patchset_files: string | null;
    patchset_hash: string | null;
    message_id: string | null;
    comment: string | null;
    start_time: string | null;
    contacts: string | null;
    log_url: string | null;
    log_excerpt: string | null;
    valid: boolean;
    misc: JSON;
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
}
