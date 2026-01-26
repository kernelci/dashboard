import type {
  RequiredStatusCount,
  ShortStatusCount,
  StatusCount,
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
  build_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
};

export interface HardwareListingResponseV2 {
  hardware: HardwareItemV2[];
}
