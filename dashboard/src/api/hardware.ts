import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  HardwareFiltersResponse,
  HardwareListingFilters,
  HardwareListingResponse,
  HardwareRevisionSelection,
  HardwareSelectorsResponse,
} from '@/types/hardware';
import type { StatusCount } from '@/types/general';
import { statusCountToShortStatusCount } from '@/utils/status';
import { MILLISECONDS_IN_ONE_HOUR } from '@/utils/date';

import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import { RequestData } from './commonRequest';

const HARDWARE_FILTERS_CACHE_DURATION = 2 * MILLISECONDS_IN_ONE_HOUR;

type HardwareListingByRevisionApiItem = {
  hardware?: string[];
  platform: string;
  build_status_summary: StatusCount;
  test_status_summary: StatusCount;
  boot_status_summary: StatusCount;
};

type HardwareListingByRevisionApiResponse = {
  hardware: HardwareListingByRevisionApiItem[];
};

const fetchHardwareListing = async (
  filters: HardwareListingFilters,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  commitsList?: string[],
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingResponse>(
    '/api/hardware/',
    {
      params: {
        startTimestampInSeconds,
        endTimestampInSeconds,
        // An empty filter is left out of the request, which the api reads as every value
        ...Object.fromEntries(
          Object.entries(filters).filter(([, value]) => value !== ''),
        ),
        ...(commitsList?.length ? { commitsList: commitsList.join(',') } : {}),
      },
    },
  );

  return data;
};

export const useHardwareListing = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  searchFrom: HardwareListingRoutesMap['search'],
  commitsList?: string[],
  enabled = true,
): UseQueryResult<HardwareListingResponse> => {
  const { checkoutOrigin, buildOrigin, testOrigin, buildLab, testLab } =
    useSearch({ from: searchFrom });
  const filters: HardwareListingFilters = {
    checkoutOrigin,
    buildOrigin,
    testOrigin,
    buildLab,
    testLab,
  };

  const queryKey = [
    'hardwareListing',
    startTimestampInSeconds,
    endTimestampInSeconds,
    filters,
    commitsList ?? null,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchHardwareListing(
        filters,
        startTimestampInSeconds,
        endTimestampInSeconds,
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
  const data = await RequestData.get<HardwareFiltersResponse>(
    '/api/hardware/filters/',
    { params: { startTimestampInSeconds, endTimestampInSeconds } },
  );

  return data;
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
    staleTime: HARDWARE_FILTERS_CACHE_DURATION,
  });
};

const fetchHardwareSelectors = async (
  origin: string,
): Promise<HardwareSelectorsResponse> => {
  const data = await RequestData.get<HardwareSelectorsResponse>(
    '/api/hardware/selectors/',
    {
      params: {
        origin,
      },
    },
  );

  return data;
};

export const useHardwareSelectors = (
  searchFrom: HardwareListingRoutesMap['search'],
): UseQueryResult<HardwareSelectorsResponse> => {
  // The revisions offered are the ones that were built, so they follow the build origin
  const { buildOrigin } = useSearch({ from: searchFrom });

  return useQuery({
    queryKey: ['hardwareSelectors', buildOrigin],
    queryFn: () => fetchHardwareSelectors(buildOrigin),
    refetchOnWindowFocus: false,
  });
};

const fetchHardwareListingByRevision = async (
  selection: HardwareRevisionSelection,
  testOrigin: string,
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingByRevisionApiResponse>(
    '/api/hardware-by-revision/',
    {
      params: {
        ...(testOrigin ? { testOrigin } : {}),
        tree_name: selection.treeName,
        git_repository_url: selection.gitRepositoryUrl,
        git_repository_branch: selection.gitBranch,
        git_commit_hash: selection.gitCommitHash,
      },
    },
  );

  return {
    hardware: data.hardware.map(item => ({
      hardware: item.hardware,
      platform: item.platform,
      build_status_summary: statusCountToShortStatusCount(
        item.build_status_summary,
      ),
      test_status_summary: statusCountToShortStatusCount(
        item.test_status_summary,
      ),
      boot_status_summary: statusCountToShortStatusCount(
        item.boot_status_summary,
      ),
    })),
  };
};

export const useHardwareListingByRevision = (
  selection: HardwareRevisionSelection | null,
  searchFrom: HardwareListingRoutesMap['search'],
): UseQueryResult<HardwareListingResponse> => {
  // This listing counts tests of a single revision, so the test origin is the only
  // one of the five filters it can honour
  const { testOrigin } = useSearch({ from: searchFrom });

  const queryKey = [
    'hardwareListingByRevision',
    testOrigin,
    selection?.treeName,
    selection?.gitRepositoryUrl,
    selection?.gitBranch,
    selection?.gitCommitHash,
    selection,
  ];

  return useQuery({
    queryKey,
    queryFn: () => {
      if (selection === null) {
        return { hardware: [] };
      }
      return fetchHardwareListingByRevision(selection, testOrigin);
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
