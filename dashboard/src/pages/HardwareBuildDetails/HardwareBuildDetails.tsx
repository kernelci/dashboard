import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useRouterState, useSearch } from '@tanstack/react-router';

import { useCallback, type JSX } from 'react';

import BuildDetails from '@/components/BuildDetails/BuildDetails';
import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';
import { RedirectFrom } from '@/types/general';
import { MemoizedHardwareBreadcrumb } from '@/components/Breadcrumb/HardwareBreadcrumb';

const HardwareBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/build/$buildId' });
  const historyState = useRouterState({ select: s => s.location.state });
  const hardwareId = historyState.id;

  const navigate = useNavigate({
    from: '/hardware/$hardwareId/build/$buildId',
  });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/hardware/$hardwareId/test/$testId',
      params: {
        testId: testId,
        hardwareId: hardwareId,
      },
      search: s => s,
    }),
    [hardwareId],
  );

  const onClickFilter = useCallback(
    (filter: PossibleTableFilters): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: filter,
            },
          };
        },
        state: { id: hardwareId, from: RedirectFrom.Hardware },
      });
    },
    [navigate, hardwareId],
  );

  return (
    <BuildDetails
      breadcrumb={
        <MemoizedHardwareBreadcrumb
          searchParams={searchParams}
          locationMessage="buildDetails.buildDetails"
        />
      }
      onClickFilter={onClickFilter}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      getTestTableRowLink={getTestTableRowLink}
    />
  );
};

export default HardwareBuildDetails;
