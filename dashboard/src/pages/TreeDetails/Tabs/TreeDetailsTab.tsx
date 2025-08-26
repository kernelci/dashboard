import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import type { JSX } from 'react';
import { useCallback, useMemo } from 'react';

import type { ITabItem, TabRightElementRecord } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import type { TreeDetailsRouteFrom } from '@/types/tree/TreeDetails';
import {
  treeDetailsFromMap,
  zPossibleTabValidator,
} from '@/types/tree/TreeDetails';

import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export interface ITreeDetailsTab {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  filterListElement?: JSX.Element;
  countElements: TabRightElementRecord;
  urlFrom: TreeDetailsRouteFrom;
}

const TreeDetailsTab = ({
  filterListElement,
  countElements,
  treeDetailsLazyLoaded,
  urlFrom,
}: ITreeDetailsTab): JSX.Element => {
  const params = useParams({
    from: urlFrom,
  });
  const { currentPageTab } = useSearch({
    from: urlFrom,
  });
  const navigate = useNavigate({ from: treeDetailsFromMap[urlFrom] });

  const treeDetailsTab: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        content: (
          <BuildTab
            treeDetailsLazyLoaded={treeDetailsLazyLoaded}
            urlFrom={urlFrom}
          />
        ),
        disabled: false,
        rightElement: countElements['buildTab'],
      },
      {
        name: 'global.boots',
        content: (
          <BootsTab
            treeDetailsLazyLoaded={treeDetailsLazyLoaded}
            urlFrom={urlFrom}
          />
        ),
        disabled: false,
        rightElement: countElements['bootTab'],
      },
      {
        name: 'global.tests',
        content: (
          <TestsTab
            treeDetailsLazyLoaded={treeDetailsLazyLoaded}
            urlFrom={urlFrom}
          />
        ),
        disabled: false,
        rightElement: countElements['testTab'],
      },
    ],
    [countElements, treeDetailsLazyLoaded, urlFrom],
  );

  const onValueChange: (value: string) => void = useCallback(
    value => {
      const validatedValue = zPossibleTabValidator.parse(value);
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            currentPageTab: validatedValue,
          };
        },
        state: s => s,
        params: params,
      });
    },
    [navigate, params],
  );

  return (
    <Tabs
      tabs={treeDetailsTab}
      filterListElement={filterListElement}
      value={currentPageTab}
      onValueChange={onValueChange}
    />
  );
};

export default TreeDetailsTab;
