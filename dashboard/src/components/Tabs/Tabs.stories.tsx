import type { Meta, StoryObj } from '@storybook/react';

import TabsComponent, { ITabItem } from './Tabs';

const meta = {
  title: 'Tabs',
  component: TabsComponent,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof TabsComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

const tabs: ITabItem[] = [
  { name: 'Boots', content: <span>Boots</span> },
  { name: 'Tests', content: <span>Tests</span>, disabled: true },
  { name: 'Builds', content: <span>Builds</span> },
];
export const Default: Story = {
  args: {
    tabs: tabs,
    defaultTab: tabs[0],
  },
};
