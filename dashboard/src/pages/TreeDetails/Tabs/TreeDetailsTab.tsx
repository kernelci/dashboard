import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import Tabs, { ITabItem } from '@/components/Tabs/Tabs';

import { zPossibleValidator } from '@/types/tree/TreeDetails';

import { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import BuildTab from './Build';
import BootsTab from './Boots';
import TestsTab from './Tests';

export interface ITreeDetailsTab {
  treeDetailsData?: ITreeDetails;
  filterListElement?: JSX.Element;
  reqFilter: Record<string, string[]>;
}

const TreeDetailsTab = ({
  treeDetailsData,
  filterListElement,
  reqFilter,
}: ITreeDetailsTab): JSX.Element => {
  const { currentTreeDetailsTab } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const buildsTab: ITabItem = {
    name: 'treeDetails.builds',
    content: (
      <BuildTab treeDetailsData={treeDetailsData} reqFilter={reqFilter} />
    ),
    disabled: false,
  };

  const bootsTab: ITabItem = {
    name: 'treeDetails.boots',
    content: <BootsTab reqFilter={reqFilter} />,
    disabled: false,
  };

  const testsTab: ITabItem = {
    name: 'treeDetails.tests',
    content: <TestsTab reqFilter={reqFilter} />,
    disabled: false,
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
