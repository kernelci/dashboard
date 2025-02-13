import type { ReactElement, JSX } from 'react';

import type { UseQueryResult } from '@tanstack/react-query';

import type { THardwareDetails } from '@/types/hardware/hardwareDetails';

import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';

export const HardwareDetailsTabsQuerySwitcher = ({
  fullDataResult,
  tabData,
  children,
}: {
  fullDataResult?: UseQueryResult<THardwareDetails>;
  tabData?:
    | THardwareDetails['builds']
    | THardwareDetails['boots']
    | THardwareDetails['tests'];
  children: ReactElement;
}): JSX.Element => {
  return (
    <QuerySwitcher
      data={tabData}
      status={fullDataResult?.status}
      customError={
        <MemoizedSectionError
          isLoading={fullDataResult?.isLoading}
          errorMessage={fullDataResult?.error?.message}
          emptyLabel={'global.error'}
        />
      }
    >
      {children}
    </QuerySwitcher>
  );
};
