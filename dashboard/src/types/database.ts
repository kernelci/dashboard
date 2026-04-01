import type { status } from '@/utils/constants/database';

export type Status = (typeof status)[number];

export type InconclusiveStatus = Exclude<Status, 'PASS' | 'FAIL'>;

// Follows kcidb schema: https://github.com/kernelci/kcidb-io/blob/8971c0269a80307ec6270ff8c78ff3816fc639f6/kcidb_io/schema/v05_03.py#L62
export type Resource = {
  name: string;
  url: string;
};
