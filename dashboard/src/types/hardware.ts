import type { StatusCount } from './general';

interface BuildCount {
  valid: number;
  invalid: number;
  null: number;
}

export interface HardwareItem {
  hardwareName: string;
  buildCount: BuildCount;
  testStatusCount: StatusCount;
  bootStatusCount: StatusCount;
}

export type HardwareListingItem = HardwareItem;

export interface HardwareListingResponse {
  hardware: HardwareListingItem[];
}

export type HardwareTableItem = HardwareItem;
