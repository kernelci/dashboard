import type { UseQueryResult } from '@tanstack/react-query';

import type { QuerySelectorStatus } from '@/components/QuerySwitcher/QuerySwitcher';
import type { UseHardwareDetailsWithoutVariant } from '@/api/hardwareDetails';
import { useHardwareDetails } from '@/api/hardwareDetails';
import type {
  HardwareSummary,
  THardwareDetails,
} from '@/types/hardware/hardwareDetails';

export type HardwareDetailsLazyLoaded = {
  summary: {
    data?: HardwareSummary;
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
  useHardwareDetailsArgs: UseHardwareDetailsWithoutVariant,
): HardwareDetailsLazyLoaded => {
  const summaryResult = useHardwareDetails({
    ...useHardwareDetailsArgs,
    variant: 'summary',
  });

  const fullResult = useHardwareDetails({
    ...useHardwareDetailsArgs,
    variant: 'full',
    enabled: !!summaryResult.data,
  });

  return {
    summary: {
      data: summaryResult.data?.summary,
      isLoading: summaryResult.isLoading,
      status: summaryResult.status,
      isPlaceholderData: summaryResult.isPlaceholderData,
      error: summaryResult.error,
    },
    full: fullResult,
    common: {
      isAllReady: !!summaryResult && !!fullResult,
      isAnyLoading: summaryResult.isLoading || fullResult.isLoading,
    },
  };
};
