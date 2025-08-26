import { useCallback, useMemo, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import {
  useNavigate,
  useParams,
  useRouterState,
  useSearch,
} from '@tanstack/react-router';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import {
  zTableFilterInfoDefault,
  type AccordionItemBuilds,
  type PossibleTableFilters,
  type TreeDetailsRouteFrom,
  treeDetailsFromMap,
} from '@/types/tree/TreeDetails';
import { getStringParam } from '@/utils/utils';
import { RedirectFrom } from '@/types/general';

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

  const { treeName, branch, id } = useRouterState({
    select: s => s.location.state,
  });
  const paramsTreeName = getStringParam(params, 'treeName');
  const paramsBranch = getStringParam(params, 'branch');
  const paramsHash =
    getStringParam(params, 'treeId') || getStringParam(params, 'hash');

  const stateIsSetted = treeName && branch && id;
  const stateParams = useMemo(
    () =>
      !stateIsSetted
        ? { treeName: paramsTreeName, branch: paramsBranch, id: paramsHash }
        : {},
    [stateIsSetted, paramsTreeName, paramsBranch, paramsHash],
  );

  const canGoDirect = paramsTreeName && paramsBranch && paramsHash;

  const getRowLink = useCallback(
    (buildId: string): LinkProps =>
      canGoDirect
        ? {
            to: '/build/$buildId',
            params: {
              buildId: buildId,
            },
            search: s => ({
              origin: s.origin,
            }),
            state: s => ({ ...s, ...stateParams, from: RedirectFrom.Tree }),
          }
        : {
            to: '/tree/$treeId/build/$buildId',
            params: {
              buildId: buildId,
              treeId: paramsHash,
            },
            search: s => ({
              origin: s.origin,
            }),
          },
    [stateParams, canGoDirect, paramsHash],
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
        params: params,
      });
    },
    [navigate, params],
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
