import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { DEFAULT_ORIGIN, type TFilter } from '@/types/general';
import { HARDWARE_LISTING_FILTER_SECTIONS } from '@/utils/constants/hardwareListingFilters';

import type {
  HardwareFiltersResponse,
  HardwareListingResponse,
  HardwareRevisionSelection,
  HardwareSelectorsResponse,
} from '@/types/hardware';

import { RequestData } from './commonRequest';

const selectedFilterValues = (section?: Record<string, boolean>): string =>
  Object.entries(section ?? {})
    .filter(([, checked]) => checked)
    .map(([key]) => key)
    .join(',');

export const hardwareListingParams = (
  diffFilter: TFilter,
): Record<string, string> =>
  Object.fromEntries(
    HARDWARE_LISTING_FILTER_SECTIONS.map(({ sectionKey, paramKey }) => [
      paramKey,
      selectedFilterValues(diffFilter[sectionKey]),
    ]),
  );

export const buildOriginForSelectors = (diffFilter: TFilter): string =>
  selectedFilterValues(diffFilter.buildOrigin) || DEFAULT_ORIGIN;

const fetchHardwareListing = async (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  params: Record<string, string>,
  commitsList?: string[],
): Promise<HardwareListingResponse> => {
  return await RequestData.get<HardwareListingResponse>('/api/hardware/', {
    params: {
      startTimestampInSeconds,
      endTimestampInSeconds,
      ...params,
      ...(commitsList?.length ? { commitsList: commitsList.join(',') } : {}),
    },
  });
};

export const useHardwareListing = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  params: Record<string, string>,
  commitsList?: string[],
  enabled = true,
): UseQueryResult<HardwareListingResponse> => {
  return useQuery({
    queryKey: [
      'hardwareListing',
      startTimestampInSeconds,
      endTimestampInSeconds,
      params,
      commitsList ?? null,
    ],
    queryFn: () =>
      fetchHardwareListing(
        startTimestampInSeconds,
        endTimestampInSeconds,
        params,
        commitsList,
      ),
    enabled,
    refetchOnWindowFocus: false,
  });
};

const fetchHardwareFilters = async (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): Promise<HardwareFiltersResponse> => {
  return await RequestData.get<HardwareFiltersResponse>(
    '/api/hardware/filters/',
    { params: { startTimestampInSeconds, endTimestampInSeconds } },
  );
};

export const useHardwareFilters = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): UseQueryResult<HardwareFiltersResponse> => {
  return useQuery({
    queryKey: [
      'hardwareFilters',
      startTimestampInSeconds,
      endTimestampInSeconds,
    ],
    queryFn: () =>
      fetchHardwareFilters(startTimestampInSeconds, endTimestampInSeconds),
    refetchOnWindowFocus: false,
  });
};

const fetchHardwareSelectors = async (
  buildOrigin: string,
): Promise<HardwareSelectorsResponse> => {
  return await RequestData.get<HardwareSelectorsResponse>(
    '/api/hardware/selectors/',
    { params: { buildOrigin } },
  );
};

export const useHardwareSelectors = (
  buildOrigin: string,
): UseQueryResult<HardwareSelectorsResponse> => {
  return useQuery({
    queryKey: ['hardwareSelectors', buildOrigin],
    queryFn: () => fetchHardwareSelectors(buildOrigin),
    refetchOnWindowFocus: false,
  });
};

const fetchHardwareListingByRevision = async (
  selection: HardwareRevisionSelection,
  params: Record<string, string>,
): Promise<HardwareListingResponse> => {
  return await RequestData.get<HardwareListingResponse>(
    '/api/hardware-by-revision/',
    {
      params: {
        ...params,
        tree_name: selection.treeName,
        git_repository_url: selection.gitRepositoryUrl,
        git_repository_branch: selection.gitBranch,
        git_commit_hash: selection.gitCommitHash,
      },
    },
  );
};

export const useHardwareListingByRevision = (
  selection: HardwareRevisionSelection | null,
  params: Record<string, string>,
): UseQueryResult<HardwareListingResponse> => {
  return useQuery({
    queryKey: ['hardwareListingByRevision', params, selection],
    queryFn: () => {
      if (selection === null) {
        return { hardware: [] };
      }
      return fetchHardwareListingByRevision(selection, params);
    },
    enabled: Boolean(
      selection?.treeName &&
        selection?.gitRepositoryUrl &&
        selection?.gitBranch &&
        selection?.gitCommitHash,
    ),
    refetchOnWindowFocus: false,
  });
};
