export type TBuildDetails = {
  timestamp: string;
  id: string;
  architecture?: string;
  checkout_id?: string;
  command?: string;
  comment?: string;
  config_name?: string;
  valid?: boolean;
  start_time?: string;
  duration?: string;
  compiler?: string;
  config_url?: string;
  log_url?: string;
  tree_name?: string;
  git_commit_hash?: string;
  git_commit_name?: string;
  git_repository_branch?: string;
  git_repository_url?: string;
  origin?: string;
  log_excerpt?: string;
  misc: IBuildDetailsMisc | null;
};

interface IBuildDetailsMisc {
  kernel_type?: string;
  dtb?: string;
  modules?: string;
  system_map?: string;
}
