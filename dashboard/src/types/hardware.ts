import type { StatusCount } from './general';

export interface HardwareFastItem {
  hardwareName: string;
}
export type HardwareFastResponse = {
  hardware: HardwareFastItem[];
};

interface BuildCount {
  valid: number;
  invalid: number;
  null: number;
}

export interface HardwareRestItem {
  buildCount: BuildCount;
  testStatusCount: StatusCount;
  bootStatusCount: StatusCount;
}

export type HardwareListingItem = HardwareRestItem & HardwareFastItem;

export interface HardwareListingResponse {
  hardware: HardwareListingItem[];
}

export type HardwareTableItem = HardwareFastItem & Partial<HardwareRestItem>;
