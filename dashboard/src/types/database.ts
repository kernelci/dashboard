import { status } from '@/utils/constants/database';

export type Status = (typeof status)[number];

export type InconclusiveStatus = Exclude<Status, 'PASS' | 'FAIL'>;
