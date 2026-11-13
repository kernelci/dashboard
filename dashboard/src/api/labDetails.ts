import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  LabAttentionItem,
  LabBootRow,
  LabBuildRow,
  LabDetailsResponse,
  LabTestRow,
} from '@/types/labDetails';

import { RequestData } from './commonRequest';

type LabWindow = {
  origin: string;
  intervalInDays: number;
};

const listingParams = ({
  origin,
  intervalInDays,
}: LabWindow): { origin: string; interval_in_days: number } => ({
  origin,
  interval_in_days: intervalInDays,
});

const labPath = (labName: string, suffix = ''): string =>
  `/api/labs/${encodeURIComponent(labName)}/${suffix}`;

const useLabWindow = (): LabWindow => {
  const { origin, intervalInDays } = useSearch({
    from: '/_main/labs/$labName',
  });
  return { origin, intervalInDays };
};

export const useLabDetails = (
  labName: string,
): UseQueryResult<LabDetailsResponse> => {
  const listing = useLabWindow();
  return useQuery({
    queryKey: ['labDetails', labName, listing],
    queryFn: () =>
      RequestData.get<LabDetailsResponse>(labPath(labName), {
        params: listingParams(listing),
      }),
    refetchOnWindowFocus: false,
  });
};

const rowParams = (
  listing: LabWindow,
  trees: string[] | undefined,
): { origin: string; interval_in_days: number; tree?: string[] } => ({
  ...listingParams(listing),
  ...(trees === undefined ? {} : { tree: trees }),
});

const useLabRows = <T>(
  kind: string,
  labName: string,
  trees: string[] | undefined,
  enabled: boolean,
  read: (listing: LabWindow) => Promise<T>,
): UseQueryResult<T> => {
  const listing = useLabWindow();
  return useQuery({
    queryKey: [kind, labName, listing, trees ?? null],
    queryFn: () => read(listing),
    enabled,
    refetchOnWindowFocus: false,
  });
};

export const useLabBuilds = (
  labName: string,
  trees: string[] | undefined,
  enabled: boolean,
): UseQueryResult<LabBuildRow[]> =>
  useLabRows('labBuilds', labName, trees, enabled, async listing => {
    const data = await RequestData.get<{ builds: LabBuildRow[] }>(
      labPath(labName, 'builds/'),
      { params: rowParams(listing, trees) },
    );
    return data.builds;
  });

export const useLabBoots = (
  labName: string,
  trees: string[] | undefined,
  enabled: boolean,
): UseQueryResult<LabBootRow[]> =>
  useLabRows('labBoots', labName, trees, enabled, async listing => {
    const data = await RequestData.get<{ boots: LabBootRow[] }>(
      labPath(labName, 'boots/'),
      { params: rowParams(listing, trees) },
    );
    return data.boots;
  });

export const useLabTests = (
  labName: string,
  trees: string[] | undefined,
  enabled: boolean,
): UseQueryResult<LabTestRow[]> =>
  useLabRows('labTests', labName, trees, enabled, async listing => {
    const data = await RequestData.get<{ tests: LabTestRow[] }>(
      labPath(labName, 'tests/'),
      { params: rowParams(listing, trees) },
    );
    return data.tests;
  });

export const useLabAttention = (
  labName: string,
  enabled: boolean,
): UseQueryResult<LabAttentionItem[]> => {
  const listing = useLabWindow();
  return useQuery({
    queryKey: ['labAttention', labName, listing],
    queryFn: async () => {
      const data = await RequestData.get<{ items: LabAttentionItem[] }>(
        labPath(labName, 'lab-attention/'),
        { params: listingParams(listing) },
      );
      return data.items;
    },
    enabled,
    refetchOnWindowFocus: false,
  });
};
