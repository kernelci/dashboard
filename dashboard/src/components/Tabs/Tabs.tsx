import { ReactElement, useMemo } from 'react';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export interface ITabItem {
  name: string;
  content: ReactElement;
  disabled?: boolean;
}

export interface ITabsComponent {
  tabs: ITabItem[];
  defaultTab: ITabItem;
}

const TabsComponent = ({ defaultTab, tabs }: ITabsComponent): JSX.Element => {
  const tabsTrigger = useMemo(
    () =>
      tabs.map(tab => (
        <TabsTrigger disabled={tab.disabled} key={tab.name} value={tab.name}>
          {tab.name}
        </TabsTrigger>
      )),
    [tabs],
  );

  const tabsContent = useMemo(
    () =>
      tabs.map(tab => (
        <TabsContent key={tab.name} value={tab.name}>
          {tab.content}
        </TabsContent>
      )),
    [tabs],
  );

  return (
    <Tabs defaultValue={defaultTab.name} className="w-full">
      <TabsList>{tabsTrigger}</TabsList>
      {tabsContent}
    </Tabs>
  );
};

export default TabsComponent;
