import { useNavigate, useSearch } from '@tanstack/react-router';

import type { ReactElement } from 'react';
import { useCallback, useMemo } from 'react';

import type { ITabItem } from '@/components/Tabs/Tabs';
import Tabs from '@/components/Tabs/Tabs';

import type { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import { zPossibleTabValidator, type TFilter } from '@/types/general';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export type TreeDetailsTabRightElement = Record<
  'global.builds' | 'global.boots' | 'global.tests',
  ReactElement
>;

export interface ITreeDetailsTab {
  treeDetailsData: ITreeDetails;
  filterListElement?: JSX.Element;
  reqFilter: TFilter;
  countElements: TreeDetailsTabRightElement;
}

const TreeDetailsTab = ({
  treeDetailsData,
  filterListElement,
  reqFilter,
  countElements,
}: ITreeDetailsTab): JSX.Element => {
  const { currentPageTab } = useSearch({
    from: '/tree/$treeId',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const treeDetailsTab: ITabItem[] = useMemo(
    () => [
      {
        name: 'global.builds',
        content: <BuildTab treeDetailsData={treeDetailsData} />,
        disabled: false,
        rightElement: countElements['global.builds'],
      },
      {
        name: 'global.boots',
        content: <BootsTab reqFilter={reqFilter} />,
        disabled: false,
        rightElement: countElements['global.boots'],
      },
      {
        name: 'global.tests',
        content: <TestsTab reqFilter={reqFilter} />,
        disabled: false,
        rightElement: countElements['global.tests'],
      },
    ],
    [countElements, reqFilter, treeDetailsData],
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
