import { useCallback, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import {
  zTableFilterInfoDefault,
  type AccordionItemBuilds,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

export interface TTreeDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
}

export function TreeDetailsBuildsTable({
  buildItems,
}: TTreeDetailsBuildsTable): JSX.Element {
  const { treeId } = useParams({ from: '/_main/tree/$treeId' });
  const { tableFilter } = useSearch({ from: '/_main/tree/$treeId' });
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const getRowLink = useCallback(
    (buildId: string): LinkProps => ({
      to: '/tree/$treeId/build/$buildId',
      params: {
        buildId: buildId,
        treeId: treeId,
      },
      search: s => s,
    }),
    [treeId],
  );

  const onClickFilter = useCallback(
    (newFilter: PossibleTableFilters): void => {
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
        state: s => s,
      });
    },
    [navigate],
  );

  return (
    <BuildsTable
      tableKey="treeDetailsBuilds"
      filter={tableFilter.buildsTable}
      buildItems={buildItems}
      onClickFilter={onClickFilter}
      getRowLink={getRowLink}
    />
  );
}
