import type { FileRoutesById, FileRoutesByTo } from '@/routeTree.gen';

type ValidHardwareNavigates<T extends keyof FileRoutesByTo> = T;
type ValidHardwareFroms<T extends keyof FileRoutesById> = T;

export type HardwareListingRoutesMap = {
  navigate: ValidHardwareNavigates<'/hardware'>;
  search: ValidHardwareFroms<'/_main/hardware'>;
};

export const hwListingCleanFullPaths = ['hardware'];
