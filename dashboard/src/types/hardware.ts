import type { RequiredStatusCount, StatusCount } from './general';

export type HardwareItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: RequiredStatusCount;
  test_status_summary: StatusCount;
  boot_status_summary: StatusCount;
};

export interface HardwareListingResponse {
  hardware: HardwareItem[];
}
