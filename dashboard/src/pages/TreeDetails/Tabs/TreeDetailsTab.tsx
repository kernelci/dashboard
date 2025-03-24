import { useNavigate, useSearch } from '@tanstack/react-router';

import type { JSX } from 'react';
import { useCallback, useMemo } from 'react';

import type { ITabItem, TabRightElementRecord } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export interface ITreeDetailsTab {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  filterListElement?: JSX.Element;
  countElements: TabRightElementRecord;
}

const TreeDetailsTab = ({
  filterListElement,
  countElements,
  treeDetailsLazyLoaded,
}: ITreeDetailsTab): JSX.Element => {
  const { currentPageTab } = useSearch({
    from: '/_main/tree/$treeId',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const treeDetailsTab: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        content: <BuildTab treeDetailsLazyLoaded={treeDetailsLazyLoaded} />,
        disabled: false,
        rightElement: countElements['buildTab'],
      },
      {
        name: 'global.boots',
        content: <BootsTab treeDetailsLazyLoaded={treeDetailsLazyLoaded} />,
        disabled: false,
        rightElement: countElements['bootTab'],
      },
      {
        name: 'global.tests',
        content: <TestsTab treeDetailsLazyLoaded={treeDetailsLazyLoaded} />,
        disabled: false,
        rightElement: countElements['testTab'],
      },
    ],
    [countElements, treeDetailsLazyLoaded],
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
      });
    },
    [navigate],
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
