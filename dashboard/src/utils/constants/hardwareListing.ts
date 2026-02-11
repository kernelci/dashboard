import type { FileRoutesById, FileRoutesByTo } from '@/routeTree.gen';

type ValidHardwareNavigates<T extends keyof FileRoutesByTo> = T;
type ValidHardwareFroms<T extends keyof FileRoutesById> = T;

export type HardwareListingRoutesMap = {
  v1: {
    navigate: ValidHardwareNavigates<'/hardware' | '/hardware/v1'>;
    search: ValidHardwareFroms<'/_main/hardware' | '/_main/hardware/v1'>;
  };
  v2: {
    navigate: ValidHardwareNavigates<'/hardware'>;
    search: ValidHardwareFroms<'/_main/hardware'>;
  };
};
