import type { RequiredStatusCount, StatusCount } from './general';

export interface HardwareItem {
  hardware_name: string;
  platform: string | string[];
  build_status_summary: RequiredStatusCount;
  test_status_summary: StatusCount;
  boot_status_summary: StatusCount;
}

export type HardwareListingItem = HardwareItem;

export interface HardwareListingResponse {
  hardware: HardwareListingItem[];
}

export type HardwareTableItem = HardwareItem;
