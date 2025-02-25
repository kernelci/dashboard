import { useCallback, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import { useSearch, useNavigate, useRouterState } from '@tanstack/react-router';

import {
  zTableFilterInfoDefault,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';
import BuildDetails from '@/components/BuildDetails/BuildDetails';

import { RedirectFrom } from '@/types/general';

import TreeBuildDetails from '@/pages/TreeBuildDetails';
import HardwareBuildDetails from '@/pages/HardwareBuildDetails';

const BuildDetailsPage = (): JSX.Element => {
  const searchParams = useSearch({ from: '/_main/build/$buildId' });
  const navigate = useNavigate({ from: '/build/$buildId' });
  const historyState = useRouterState({ select: s => s.location.state });

  const getTestTableRowLink = useCallback(
    (testId: string): LinkProps => ({
      to: '/test/$testId',
      params: {
        testId: testId,
      },
      search: s => s,
    }),
    [],
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
        state: historyState,
      });
    },
    [navigate, historyState],
  );

  if (historyState.id !== undefined) {
    if (historyState.from === RedirectFrom.Tree) {
      return <TreeBuildDetails />;
    }

    if (historyState.from === RedirectFrom.Hardware) {
      return <HardwareBuildDetails />;
    }
  }

  return (
    <BuildDetails
      onClickFilter={onClickFilter}
      tableFilter={searchParams.tableFilter ?? zTableFilterInfoDefault}
      getTestTableRowLink={getTestTableRowLink}
    />
  );
};

export default BuildDetailsPage;
