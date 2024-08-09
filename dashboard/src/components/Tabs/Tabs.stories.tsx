import type { Meta, StoryObj } from '@storybook/react';

import TabsComponent, { ITabItem } from './Tabs';

const meta = {
  title: 'Components/Tabs',
  component: TabsComponent,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof TabsComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

const tabs: ITabItem[] = [
  { name: 'treeDetails.boots', content: <span>Boots</span> },
  { name: 'treeDetails.tests', content: <span>Tests</span>, disabled: true },
  { name: 'treeDetails.builds', content: <span>Builds</span> },
];
export const Default: Story = {
  args: {
    tabs: tabs,
    defaultTab: 'treeDetails.boots',
  },
};
