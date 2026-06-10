import type { FileRoutesById, FileRoutesByTo } from '@/routeTree.gen';

type ValidTreeNavigates<T extends keyof FileRoutesByTo> = T;
type ValidTreeFroms<T extends keyof FileRoutesById> = T;

export type TreeListingRoutesMap = {
  navigate: ValidTreeNavigates<'/tree'>;
  search: ValidTreeFroms<'/_main/tree'>;
};

export const treeListingCleanFullPaths = ['tree'];
