import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import Tabs, { ITabItem } from '@/components/Tabs/Tabs';

import { zPossibleValidator } from '@/types/tree/TreeDetails';

import { ITreeDetails } from '@/pages/TreeDetails/TreeDetails';

import TreeDetailsBuildTab from './TreeDetails/TreeDetailsBuildTab';
import BootsTab from './Boots';

export interface ITreeDetailsBuildTab {
  treeDetailsData?: ITreeDetails;
  filterListElement?: JSX.Element;
}

const TreeDetailsTab = ({
  treeDetailsData,
  filterListElement,
}: ITreeDetailsBuildTab): JSX.Element => {
  const { currentTreeDetailsTab } = useSearch({
    from: '/tree/$treeId/',
  });
  const navigate = useNavigate({ from: '/tree/$treeId' });
  const buildsTab: ITabItem = {
    name: 'treeDetails.builds',
    content: <TreeDetailsBuildTab treeDetailsData={treeDetailsData} />,
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

  const bootsTab: ITabItem = {
    name: 'treeDetails.boots',
    content: <BootsTab />,
    disabled: false,
  };

  const testsTab: ITabItem = {
    name: 'treeDetails.tests',
    content: <></>,
    disabled: true,
  };

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
