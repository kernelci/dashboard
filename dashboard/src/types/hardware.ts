import type {
  RequiredStatusCount,
  StatusCount,
  StatusCountV2,
} from './general';

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

export type HardwareItemV2 = {
  hardware?: string[];
  platform: string;
  build_status_summary: StatusCountV2;
  test_status_summary: StatusCountV2;
  boot_status_summary: StatusCountV2;
};

export interface HardwareListingResponseV2 {
  hardware: HardwareItemV2[];
}
