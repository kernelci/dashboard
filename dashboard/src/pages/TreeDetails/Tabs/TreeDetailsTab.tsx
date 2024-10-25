import { useNavigate, useSearch } from '@tanstack/react-router';

import { ReactElement, useCallback } from 'react';

import Tabs, { ITabItem } from '@/components/Tabs/Tabs';

import { zPossibleValidator } from '@/types/tree/TreeDetails';

import { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import { MessagesKey } from '@/locales/messages';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export type TreeDetailsTabRightElement = Record<
  Extract<
    MessagesKey,
    'treeDetails.builds' | 'treeDetails.boots' | 'treeDetails.tests'
  >,
  ReactElement
>;

export interface ITreeDetailsTab {
  treeDetailsData?: ITreeDetails;
  filterListElement?: JSX.Element;
  reqFilter: Record<string, string[]>;
  countElements: TreeDetailsTabRightElement;
}

const TreeDetailsTab = ({
  treeDetailsData,
  filterListElement,
  reqFilter,
  countElements,
}: ITreeDetailsTab): JSX.Element => {
  const { currentTreeDetailsTab } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const buildsTab: ITabItem = {
    name: 'treeDetails.builds',
    content: <BuildTab treeDetailsData={treeDetailsData} />,
    disabled: false,
    rightElement: countElements['treeDetails.builds'],
  };

  const bootsTab: ITabItem = {
    name: 'treeDetails.boots',
    content: <BootsTab reqFilter={reqFilter} />,
    disabled: false,
    rightElement: countElements['treeDetails.boots'],
  };

  const testsTab: ITabItem = {
    name: 'treeDetails.tests',
    content: <TestsTab reqFilter={reqFilter} />,
    disabled: false,
    rightElement: countElements['treeDetails.tests'],
  };

  const onValueChange: (value: string) => void = useCallback(
    value => {
      const validatedValue = zPossibleValidator.parse(value);
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            currentTreeDetailsTab: validatedValue,
          };
        },
      });
    },
    [navigate],
  );

  const treeDetailsTab = [buildsTab, bootsTab, testsTab];
  return (
    <Tabs
      tabs={treeDetailsTab}
      filterListElement={filterListElement}
      value={currentTreeDetailsTab}
      onValueChange={onValueChange}
    />
  );
};

export default TreeDetailsTab;
