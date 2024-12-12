import { useCallback } from 'react';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import {
  zTableFilterInfoDefault,
  type AccordionItemBuilds,
  type BuildsTableFilter,
} from '@/types/tree/TreeDetails';

export interface TTreeDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
}

export function TreeDetailsBuildsTable({
  buildItems,
}: TTreeDetailsBuildsTable): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId' });
  const { tableFilter } = useSearch({ from: '/tree/$treeId' });
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const navigateToBuildDetails = useCallback(
    (buildId: string) => {
      navigate({
        to: `/tree/${treeId}/build/${buildId}`,
        params: { treeId },
        search: prev => prev,
      });
    },
    [navigate, treeId],
  );

  const onClickFilter = useCallback(
    (newFilter: BuildsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              buildsTable: newFilter,
            },
          };
        },
      });
    },
    [navigate],
  );

  return (
    <BuildsTable
      tableKey="treeDetailsBuilds"
      onClickShowBuild={navigateToBuildDetails}
      filter={tableFilter.buildsTable}
      buildItems={buildItems}
      onClickFilter={onClickFilter}
    />
  );
}
