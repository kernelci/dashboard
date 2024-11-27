import type { Meta, StoryObj } from '@storybook/react';

import type { ITabItem } from './Tabs';
import TabsComponent from './Tabs';

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
  { name: 'global.boots', content: <span>Boots</span> },
  { name: 'global.tests', content: <span>Tests</span>, disabled: true },
  { name: 'global.builds', content: <span>Builds</span> },
];
export const Default: Story = {
  args: {
    tabs: tabs,
    defaultTab: 'global.boots',
  },
};
