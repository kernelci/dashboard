import type { StatusCount } from './general';

export type BuildCount = {
  valid: number;
  invalid: number;
  null: number;
};

export interface HardwareItem {
  hardware_name: string;
  build_status_summary: BuildCount;
  test_status_summary: StatusCount;
  boot_status_summary: StatusCount;
}

export type HardwareListingItem = HardwareItem;

export interface HardwareListingResponse {
  hardware: HardwareListingItem[];
}

export type HardwareTableItem = HardwareItem;
