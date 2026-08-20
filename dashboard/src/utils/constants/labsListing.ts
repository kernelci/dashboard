import type { FileRoutesById, FileRoutesByTo } from '@/routeTree.gen';

type ValidLabsNavigates<T extends keyof FileRoutesByTo> = T;
type ValidLabsFroms<T extends keyof FileRoutesById> = T;

export type LabsListingRoutesMap = {
  navigate: ValidLabsNavigates<'/labs'>;
  search: ValidLabsFroms<'/_main/labs'>;
};

export const labsListingCleanFullPaths = ['labs'];
