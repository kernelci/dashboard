import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useRouterState, useSearch } from '@tanstack/react-router';

import { useCallback, type JSX } from 'react';

import { useSearchStore } from '@/hooks/store/useSearchStore';

import BuildDetails from '@/components/BuildDetails/BuildDetails';
import {
  zTableFilterInfoDefault,
  type TableStatusOption,
} from '@/types/tree/TreeDetails';
import { toggleTableStatus } from '@/utils/tableStatusFilter';
import { RedirectFrom } from '@/types/general';
import { MemoizedHardwareBreadcrumb } from '@/components/Breadcrumb/HardwareBreadcrumb';

const HardwareBuildDetails = (): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/build/$buildId' });
  const hardwareId = useRouterState({ select: s => s.location.state.id });
  const previousSearch = useSearchStore(s => s.previousSearch);

  const navigate = useNavigate({
    from: '/hardware/$hardwareId/build/$buildId/',
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

  const onToggleFilter = useCallback(
    (option: TableStatusOption): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              testsTable: toggleTableStatus(
                previousParams.tableFilter?.testsTable,
                option,
              ),
            },
          };
        },
        state: { id: hardwareId, from: RedirectFrom.Hardware },
        resetScroll: false,
      });
    },
    [navigate, hardwareId],
  );

  return (
    <BuildDetails
      breadcrumb={
        <MemoizedHardwareBreadcrumb
          searchParams={previousSearch}
          locationMessage="buildDetails.buildDetails"
        />
      }
      onToggleFilter={onToggleFilter}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      getTestTableRowLink={getTestTableRowLink}
    />
  );
};

export default HardwareBuildDetails;
