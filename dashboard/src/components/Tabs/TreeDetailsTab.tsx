import Tabs, { ITabItem } from '@/components/Tabs/Tabs';
import { ITreeDetails } from '@/routes/TreeDetails/TreeDetails';

import TreeDetailsBuildTab from './TreeDetails/TreeDetailsBuildTab';

export interface ITreeDetailsBuildTab {
  treeDetailsData?: ITreeDetails;
  filterListElement?: JSX.Element;
}

const TreeDetailsTab = ({
  treeDetailsData,
  filterListElement,
}: ITreeDetailsBuildTab): JSX.Element => {
  const buildsTab: ITabItem = {
    name: 'treeDetails.builds',
    content: <TreeDetailsBuildTab treeDetailsData={treeDetailsData} />,
    disabled: false,
  };

  const bootsTab: ITabItem = {
    name: 'treeDetails.boots',
    content: <></>,
    disabled: true,
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
      defaultTab={treeDetailsTab[0]}
      filterListElement={filterListElement}
    />
  );
};

export default TreeDetailsTab;
