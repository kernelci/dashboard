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
  misc: JSON | null;
};

export type TreeDetails = {
  builds: TreeDetailsBuild[];
  summary: {
    builds: {
      valid: number;
      invalid: number;
      null: number;
    };
    configs: object;
    architectures: object;
  };
};
