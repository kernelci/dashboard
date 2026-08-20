import type { UseQueryResult } from '@tanstack/react-query';

import type { QuerySelectorStatus } from '@/components/QuerySwitcher/QuerySwitcher';
import {
  useHardwareDetails,
  type UseHardwareDetailsWithoutVariant,
} from '@/api/hardwareDetails';
import type {
  HardwareDetailsSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

export type HardwareDetailsLazyLoaded = {
  summary: {
    data?: HardwareDetailsSummary;
    isLoading: boolean;
    status: QuerySelectorStatus;
    error: UseQueryResult['error'];
    isPlaceholderData: boolean;
  };
  full: UseQueryResult<THardwareDetails>;
  common: {
    isAllReady: boolean;
    isAnyLoading: boolean;
  };
};

export const useHardwareDetailsLazyLoadQuery = (
  args: UseHardwareDetailsWithoutVariant,
): HardwareDetailsLazyLoaded => {
  const summaryQuery = useHardwareDetails({ ...args, variant: 'summary-data' });
  const commonQuery = useHardwareDetails({ ...args, variant: 'common' });
  const filtersQuery = useHardwareDetails({ ...args, variant: 'filters' });

  const isLoading =
    summaryQuery.isLoading || commonQuery.isLoading || filtersQuery.isLoading;
  const error =
    summaryQuery.error ?? commonQuery.error ?? filtersQuery.error ?? null;

  const data: HardwareDetailsSummary | undefined =
    summaryQuery.data && commonQuery.data && filtersQuery.data
      ? {
          summary: summaryQuery.data.summary,
          common: commonQuery.data.common,
          filters: filtersQuery.data.filters,
        }
      : undefined;

  const status: QuerySelectorStatus = isLoading
    ? 'pending'
    : error
      ? 'error'
      : data
        ? 'success'
        : 'pending';

  const fullResult = useHardwareDetails({
    ...args,
    variant: 'full',
    enabled: (args.enabled ?? true) && !!data,
  });

  return {
    summary: {
      data,
      isLoading,
      status,
      isPlaceholderData: summaryQuery.isPlaceholderData,
      error,
    },
    full: fullResult,
    common: {
      isAllReady: !!data && !!fullResult.data,
      isAnyLoading: isLoading || fullResult.isLoading,
    },
  };
};
