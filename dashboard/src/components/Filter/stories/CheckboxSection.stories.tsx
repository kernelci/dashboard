import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import CheckboxSection from '../CheckboxSection';

const ActionsData = {
  onClickItem: fn(),
};

const meta: Meta<typeof CheckboxSection> = {
  title: 'Filter CheckboxSection',
  component: CheckboxSection,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  args: {
    ...ActionsData,
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    items: ['linux-5.15.y', 'Status:failed', 'Status: Warnings'],
    title: 'Branch',
    subtitle: 'Please select one or more Branches',
  },
};

export const WithSubSections: Story = {
  args: {
    title: 'Error Summary',
    subsections: [
      {
        title: 'Errors',
        items: ['linux-5.15.y', 'Status:failed', 'Status: Warnings'],
        onClickItem: ActionsData.onClickItem,
      },
      {
        title: 'Warnings',
        items: ['linux-5.15.y', 'Status:failed', 'Status: Warnings'],
        onClickItem: ActionsData.onClickItem,
      },
    ],
  },
};
