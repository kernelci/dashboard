type TreeDetailsBuild = {
  id: string;
  architecture: string;
  config_name: string;
  valid: boolean;
  start_time: string;
  duration: string;
  compiler: string;
  config_url: string;
  log_url: string;
  git_repository_branch: string;
  git_repository_url: string;
  status: {
    fail_tests: number;
    error_tests: number;
    miss_tests: number;
    pass_tests: number;
    done_tests: number;
    skip_tests: number;
    null_tests: number;
    total_tests: number;
  };
  misc: ITreeDetailsMisc | null;
};

interface ITreeDetailsMisc {
  kernel_type?: string;
  dtb?: string;
  modules?: string;
  system_map?: string;
}

export type AccordionItemBuilds = {
  config?: string;
  compiler?: string;
  date?: string;
  buildErrors?: number;
  buildTime?: string;
  status?: 'valid' | 'invalid';
  testStatus?: {
    failTests: number;
    errorTests: number;
    passTests: number;
    skipTests: number;
  };
  kernelImage?: string;
  buildLogs?: string;
  kernelConfig?: string;
  dtb?: string;
  systemMap?: string;
  modules?: string;
};

export type TreeDetails = {
  builds: TreeDetailsBuild[];
  summary: {
    builds: Results;
    configs: object;
    architectures: object;
  };
};

export type Results = {
  valid: number;
  invalid: number;
  null: number;
};
export interface TTreeDetailsFilter
  extends Partial<{
    [K in keyof Omit<
      TreeDetailsBuild,
      'test_status' | 'misc' | 'valid'
    >]: TreeDetailsBuild[K][];
  }> {
  valid?: string[];
}
