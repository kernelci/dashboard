import { ComponentProps, ReactElement, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { MessagesKey } from '@/locales/messages';

export interface ITabItem {
  name: MessagesKey;
  content: ReactElement;
  disabled?: boolean;
}

type TabsProp = ComponentProps<typeof Tabs>;

export interface ITabsComponent {
  tabs: ITabItem[];
  defaultTab?: string;
  filterListElement?: JSX.Element;
  onValueChange?: TabsProp['onValueChange'];
  value?: TabsProp['value'];
}

const TabsComponent = ({
  defaultTab,
  tabs,
  filterListElement,
  onValueChange,
  value,
}: ITabsComponent): JSX.Element => {
  const tabsTrigger = useMemo(
    () =>
      tabs.map(tab => (
        <TabsTrigger
          className="border-b-2 border-transparent bg-transparent px-4 text-lg data-[state=active]:border-lightBlue"
          disabled={tab.disabled}
          key={tab.name}
          value={tab.name}
        >
          <FormattedMessage id={tab.name} />
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
    <Tabs
      onValueChange={onValueChange}
      value={value}
      defaultValue={defaultTab}
      className="w-full"
    >
      <TabsList className="w-full justify-start bg-transparent">
        {tabsTrigger}
      </TabsList>
      <div className="border-t border-darkGray py-6">{filterListElement}</div>

      {tabsContent}
    </Tabs>
  );
};

export default TabsComponent;
