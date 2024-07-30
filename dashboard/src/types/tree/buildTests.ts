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
