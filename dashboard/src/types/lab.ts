import type { ShortStatusCount } from './general';

export type LabListingItem = {
  lab_name: string;
  build_status_summary: ShortStatusCount;
  boot_status_summary: ShortStatusCount;
  test_status_summary: ShortStatusCount;
};

export interface LabListingResponse {
  labs: LabListingItem[];
}
