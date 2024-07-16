import Tabs, { ITabItem } from '@/components/Tabs/Tabs';

const TreeDetailsTab = (): JSX.Element => {
  return <Tabs tabs={treeDetailsTab} defaultTab={treeDetailsTab[0]} />;
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

const buildsTab: ITabItem = {
  name: 'treeDetails.builds',
  content: <></>,
  disabled: false,
};

const treeDetailsTab = [buildsTab, bootsTab, testsTab];

export default TreeDetailsTab;
