import type { FileRoutesById, FileRoutesByTo } from '@/routeTree.gen';

import type { HardwareListingFilters } from '@/types/hardware';
import { DEFAULT_ORIGIN } from '@/types/general';

/** KCI treats maestro checkouts and builds as the baseline, while every test origin
 * and lab is shown until the user narrows it down. */
export const DEFAULT_HARDWARE_LISTING_FILTERS: HardwareListingFilters = {
  checkoutOrigin: DEFAULT_ORIGIN,
  buildOrigin: DEFAULT_ORIGIN,
  testOrigin: '',
  buildLab: '',
  testLab: '',
};

type ValidHardwareNavigates<T extends keyof FileRoutesByTo> = T;
type ValidHardwareFroms<T extends keyof FileRoutesById> = T;

export type HardwareListingRoutesMap = {
  navigate: ValidHardwareNavigates<'/hardware'>;
  search: ValidHardwareFroms<'/_main/hardware'>;
};

export const hwListingCleanFullPaths = ['hardware'];
