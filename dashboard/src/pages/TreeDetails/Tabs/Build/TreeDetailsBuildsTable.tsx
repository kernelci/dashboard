import { useCallback, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import {
  zTableFilterInfoDefault,
  type AccordionItemBuilds,
  type PossibleTableFilters,
  type TreeDetailsRouteFrom,
  treeDetailsFromMap,
} from '@/types/tree/TreeDetails';
import { getStringParam } from '@/utils/utils';

export interface TTreeDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
  urlFrom: TreeDetailsRouteFrom;
}

export function TreeDetailsBuildsTable({
  buildItems,
  urlFrom,
}: TTreeDetailsBuildsTable): JSX.Element {
  const params = useParams({ from: urlFrom });
  const { tableFilter } = useSearch({ from: urlFrom });
  const navigate = useNavigate({ from: treeDetailsFromMap[urlFrom] });

  const treeId =
    getStringParam(params, 'treeId') || getStringParam(params, 'hash');

  const getRowLink = useCallback(
    (buildId: string): LinkProps => ({
      to: '/tree/$treeId/build/$buildId',
      params: {
        buildId: buildId,
        treeId: treeId,
      },
      search: s => ({
        origin: s.origin,
      }),
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
