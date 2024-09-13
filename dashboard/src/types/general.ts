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
