import type { ComponentProps, ReactElement, JSX } from 'react';
import { useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { MessagesKey } from '@/locales/messages';

export type TabRightElementRecord = Record<
  'buildTab' | 'bootTab' | 'testTab',
  ReactElement
>;

export interface ITabItem {
  name: MessagesKey;
  content: ReactElement;
  disabled?: boolean;
  rightElement?: ReactElement;
}

type TabsProp = ComponentProps<typeof Tabs>;

export interface ITabsComponent {
  tabs: ITabItem[];
  defaultTab?: string;
  filterListElement?: JSX.Element;
  onValueChange?: TabsProp['onValueChange'];
  value?: TabsProp['value'];
  headerExtra?: ReactElement;
}

const TabsComponent = ({
  defaultTab,
  tabs,
  filterListElement,
  onValueChange,
  value,
  headerExtra,
}: ITabsComponent): JSX.Element => {
  const tabsTrigger = useMemo(
    () =>
      tabs.map(tab => (
        <TabsTrigger
          className="data-[state=active]:border-blue border-b-2 border-transparent bg-transparent px-4 text-lg"
          disabled={tab.disabled}
          key={tab.name}
          value={tab.name}
        >
          <FormattedMessage id={tab.name} />
          <div className="pl-2">{tab.rightElement}</div>
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
      <div className="bg-light-gray sticky top-18 z-5 flex flex-col gap-6 rounded-md pt-6 pb-6">
        <div className="flex w-full flex-wrap justify-between gap-6">
          <TabsList className="border-dark-gray flex-1 items-baseline justify-start rounded-none border-b bg-transparent">
            {tabsTrigger}
          </TabsList>
          {headerExtra}
        </div>
        {filterListElement}
      </div>

      {tabsContent}
    </Tabs>
  );
};

export default TabsComponent;
