import { Status } from './database';

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
  status: Status;
  start_time: string;
  duration: string;
};

export type TBuildTests = {
  current_path: string;
  start_time: string;
  origins: string[];
  fail_tests: number;
  error_tests: number;
  miss_tests: number;
  pass_tests: number;
  done_tests: number;
  skip_tests: number;
  null_tests: number;
  total_tests: number;
};

export type TIssue = {
  id: string;
  comment?: string;
  report_url?: string;
  present?: boolean;
  incident_id: string;
};
