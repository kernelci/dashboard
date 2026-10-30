import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  HardwareListingResponse,
  HardwareRegistrySyncResponse,
  HardwareRegistryFilterOptions,
  HardwareRevisionSelection,
  HardwareSelectorsResponse,
} from '@/types/hardware';
import {
  registryFilterToParams,
  type TRegistryFilter,
} from '@/pages/Hardware/registryFilters';
import type { StatusCount } from '@/types/general';
import { statusCountToShortStatusCount } from '@/utils/status';

import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import { RequestData } from './commonRequest';

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
  origin: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  commitsList?: string[],
  registryFilter?: TRegistryFilter,
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingResponse>(
    '/api/hardware/',
    {
      params: {
        startTimestampInSeconds,
        endTimestampInSeconds,
        origin,
        ...(commitsList?.length ? { commitsList: commitsList.join(',') } : {}),
        ...registryFilterToParams(registryFilter ?? {}),
      },
    },
  );

  return data;
};

const fetchHardwareRegistrySync =
  async (): Promise<HardwareRegistrySyncResponse> => {
    return RequestData.get<HardwareRegistrySyncResponse>(
      '/api/hardware/registry-sync/',
    );
  };

export const useHardwareRegistrySync =
  (): UseQueryResult<HardwareRegistrySyncResponse> => {
    return useQuery({
      queryKey: ['hardwareRegistrySync'],
      queryFn: fetchHardwareRegistrySync,
      refetchOnWindowFocus: false,
    });
  };

export const useHardwareListing = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  searchFrom: HardwareListingRoutesMap['search'],
  commitsList?: string[],
  enabled = true,
): UseQueryResult<HardwareListingResponse> => {
  const { origin, registryFilter } = useSearch({ from: searchFrom });

  const queryKey = [
    'hardwareListing',
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
    commitsList ?? null,
    registryFilter,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchHardwareListing(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
        commitsList,
        registryFilter,
      ),
    enabled,
    refetchOnWindowFocus: false,
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

const fetchHardwareRegistryFilterOptions = async (
  origin: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  selection: HardwareRevisionSelection | null,
): Promise<HardwareRegistryFilterOptions> =>
  RequestData.get<HardwareRegistryFilterOptions>(
    '/api/hardware/registry-filters/',
    {
      params: {
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
        ...(selection
          ? {
              tree_name: selection.treeName,
              git_repository_url: selection.gitRepositoryUrl,
              git_repository_branch: selection.gitBranch,
              git_commit_hash: selection.gitCommitHash,
            }
          : {}),
      },
    },
  );

export const useHardwareRegistryFilterOptions = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  searchFrom: HardwareListingRoutesMap['search'],
): UseQueryResult<HardwareRegistryFilterOptions> => {
  const { origin, treeName, gitRepositoryUrl, gitBranch, gitCommitHash } =
    useSearch({ from: searchFrom });
  const selection: HardwareRevisionSelection | null =
    treeName && gitRepositoryUrl && gitBranch && gitCommitHash
      ? { treeName, gitRepositoryUrl, gitBranch, gitCommitHash }
      : null;

  return useQuery({
    queryKey: [
      'hardwareRegistryFilterOptions',
      origin,
      startTimestampInSeconds,
      endTimestampInSeconds,
      selection,
    ],
    queryFn: () =>
      fetchHardwareRegistryFilterOptions(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
        selection,
      ),
    refetchOnWindowFocus: false,
  });
};

export const useHardwareSelectors = (
  searchFrom: HardwareListingRoutesMap['search'],
): UseQueryResult<HardwareSelectorsResponse> => {
  const { origin } = useSearch({ from: searchFrom });

  return useQuery({
    queryKey: ['hardwareSelectors', origin],
    queryFn: () => fetchHardwareSelectors(origin),
    refetchOnWindowFocus: false,
  });
};

const fetchHardwareListingByRevision = async (
  selection: HardwareRevisionSelection,
  origin: string,
  registryFilter: TRegistryFilter,
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingByRevisionApiResponse>(
    '/api/hardware-by-revision/',
    {
      params: {
        origin,
        tree_name: selection.treeName,
        git_repository_url: selection.gitRepositoryUrl,
        git_repository_branch: selection.gitBranch,
        git_commit_hash: selection.gitCommitHash,
        ...registryFilterToParams(registryFilter),
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
  const { origin, registryFilter } = useSearch({ from: searchFrom });

  const queryKey = [
    'hardwareListingByRevision',
    origin,
    selection?.treeName,
    selection?.gitRepositoryUrl,
    selection?.gitBranch,
    selection?.gitCommitHash,
    selection,
    registryFilter,
  ];

  return useQuery({
    queryKey,
    queryFn: () => {
      if (selection === null) {
        return { hardware: [] };
      }
      return fetchHardwareListingByRevision(selection, origin, registryFilter);
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
