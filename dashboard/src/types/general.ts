import type { Status } from './database';

type IncidentsInfo = { incidentsCount: number };

export type TPathTests = {
  path_group: string;
  fail_tests: number;
  error_tests: number;
  miss_tests: number;
  pass_tests: number;
  done_tests: number;
  skip_tests: number;
  null_tests: number;
  total_tests: number;
  individual_tests: TIndividualTest[];
};

export type TIndividualTest = {
  id: string;
  path: string;
  status?: Status;
  start_time: string;
  duration: string;
  hardware?: string[];
};

export type TIssue = {
  id: string;
  comment?: string;
  report_url?: string;
  incidents_info: IncidentsInfo;
};

export type TestHistory = {
  startTime: string;
  status: Status;
  path: string;
  id: string;
  duration?: number;
  hardware?: string[];
};

interface ITreeDetailsMisc {
  kernel_type?: string;
  dtb?: string;
  modules?: string;
  system_map?: string;
}

export type BuildsTabBuild = {
  id: string;
  architecture: string;
  config_name: string;
  valid: boolean | null;
  start_time: string;
  duration: string;
  compiler: string;
  config_url: string;
  log_url: string;
  git_repository_branch: string;
  git_repository_url: string;
  misc: ITreeDetailsMisc | null;
};

export type BuildStatus = {
  valid: number;
  invalid: number;
  null: number;
};

export type Architecture = Record<
  string,
  BuildStatus & {
    compilers: string[];
  }
>;
