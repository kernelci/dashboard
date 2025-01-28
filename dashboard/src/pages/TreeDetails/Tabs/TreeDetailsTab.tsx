import { useNavigate, useSearch } from '@tanstack/react-router';

import type { ReactElement } from 'react';
import { useCallback, useMemo } from 'react';

import type { ITabItem } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { TreeDetailsLazyLoaded } from '@/hooks/useTreeDetailsLazyLoadQuery';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export type TreeDetailsTabRightElement = Record<
  'global.builds' | 'global.boots' | 'global.tests',
  ReactElement
>;

export interface ITreeDetailsTab {
  treeDetailsLazyLoaded: TreeDetailsLazyLoaded;
  filterListElement?: JSX.Element;
  countElements: TreeDetailsTabRightElement;
}

const TreeDetailsTab = ({
  filterListElement,
  countElements,
  treeDetailsLazyLoaded,
}: ITreeDetailsTab): JSX.Element => {
  const { currentPageTab } = useSearch({
    from: '/tree/$treeId',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const treeDetailsTab: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        content: <BuildTab treeDetailsLazyLoaded={treeDetailsLazyLoaded} />,
        disabled: false,
        rightElement: countElements['global.builds'],
      },
      {
        name: 'global.boots',
        content: <BootsTab treeDetailsLazyLoaded={treeDetailsLazyLoaded} />,
        disabled: false,
        rightElement: countElements['global.boots'],
      },
      {
        name: 'global.tests',
        content: <TestsTab treeDetailsLazyLoaded={treeDetailsLazyLoaded} />,
        disabled: false,
        rightElement: countElements['global.tests'],
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
