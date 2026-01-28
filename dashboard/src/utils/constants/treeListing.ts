import type { FileRoutesById, FileRoutesByTo } from '@/routeTree.gen';

type ValidTreeNavigates<T extends keyof FileRoutesByTo> = T;
type ValidTreeFroms<T extends keyof FileRoutesById> = T;

export type TreeListingRoutesMap = {
  v1: {
    navigate: ValidTreeNavigates<'/tree' | '/tree/v1'>;
    search: ValidTreeFroms<'/_main/tree' | '/_main/tree/v1'>;
  };
  v2: {
    navigate: ValidTreeNavigates<'/tree' | '/tree/v2'>;
    search: ValidTreeFroms<'/_main/tree' | '/_main/tree/v2'>;
  };
};
