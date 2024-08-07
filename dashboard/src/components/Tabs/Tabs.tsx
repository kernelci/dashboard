import { ReactElement, useMemo } from 'react';

import classNames from 'classnames';

import { FormattedMessage } from 'react-intl';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export interface ITabItem {
  name: MessagesKey;
  content: ReactElement;
  disabled?: boolean;
}

export interface ITabsComponent {
  tabs: ITabItem[];
  defaultTab: ITabItem;
  filterListElement?: JSX.Element;
}

const TabsComponent = ({
  defaultTab,
  tabs,
  filterListElement,
}: ITabsComponent): JSX.Element => {
  const tabsTrigger = useMemo(
    () =>
      tabs.map(tab => (
        <TabsTrigger
          className={classNames('bg-transparent px-4 text-lg', {
            'border-b-2 border-lightBlue': !tab.disabled,
          })}
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
    <Tabs defaultValue={defaultTab.name} className="w-full">
      <TabsList className="w-full justify-start">{tabsTrigger}</TabsList>
      <div className="py-6">{filterListElement}</div>

      {tabsContent}
    </Tabs>
  );
};

export default TabsComponent;
