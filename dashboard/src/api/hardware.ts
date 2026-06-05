import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type {
  HardwareListingResponse,
  HardwareRevisionSelection,
  HardwareSelectorsResponse,
} from '@/types/hardware';

import type { HardwareListingRoutesMap } from '@/utils/constants/hardwareListing';

import { RequestData } from './commonRequest';

const fetchHardwareListing = async (
  origin: string,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingResponse>(
    '/api/hardware/',
    {
      params: {
        startTimestampInSeconds,
        endTimestampInSeconds,
        origin,
      },
    },
  );

  return data;
};

export const useHardwareListing = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  searchFrom: HardwareListingRoutesMap['v1']['search'],
): UseQueryResult<HardwareListingResponse> => {
  const { origin } = useSearch({ from: searchFrom });

  const queryKey = [
    'hardwareListing',
    startTimestampInSeconds,
    endTimestampInSeconds,
    origin,
  ];

  return useQuery({
    queryKey,
    queryFn: () =>
      fetchHardwareListing(
        origin,
        startTimestampInSeconds,
        endTimestampInSeconds,
      ),
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

export const useHardwareSelectors = (
  searchFrom: HardwareListingRoutesMap['v2']['search'],
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
): Promise<HardwareListingResponse> => {
  const data = await RequestData.get<HardwareListingResponse>(
    '/api/hardware-by-revision/',
    {
      params: {
        origin,
        tree_name: selection.treeName,
        git_repository_url: selection.gitRepositoryUrl,
        git_repository_branch: selection.gitBranch,
        git_commit_hash: selection.gitCommitHash,
      },
    },
  );

  return data;
};

export const useHardwareListingByRevision = (
  selection: HardwareRevisionSelection | null,
  searchFrom: HardwareListingRoutesMap['v2']['search'],
): UseQueryResult<HardwareListingResponse> => {
  const { origin } = useSearch({ from: searchFrom });

  const queryKey = [
    'hardwareListingByRevision',
    origin,
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
      return fetchHardwareListingByRevision(selection, origin);
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
