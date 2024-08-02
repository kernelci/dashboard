import { status } from '../utils/constants/database';

export type Status = (typeof status)[number];

export type ErrorStatus = Exclude<Status, 'PASS' | 'SKIP' | 'DONE'>;
