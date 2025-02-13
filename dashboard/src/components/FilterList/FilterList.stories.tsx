import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { IntlProvider } from 'react-intl';

import type { JSX } from 'react';

import { LOCALES } from '../../locales/constants';

import { messages } from '../../locales/messages';

import FilterList from './FilterList';

const ActionsData = {
  onClickItem: fn(),
  onClickCleanAll: fn(),
};

const meta: Meta<typeof FilterList> = {
  title: 'Components/FilterList',
  component: FilterList,
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
  },
  decorators: [
    (story): JSX.Element => (
      <IntlProvider messages={messages[LOCALES.EN_US]} locale={LOCALES.EN_US}>
        {story()}
      </IntlProvider>
    ),
  ],
};

export const MultipleLines: Story = {
  args: {
    items: [
      'linux-5.15.y',
      'Status:failed',
      'Status: Warnings',
      'Status:failed',
      'Status: Warnings',
    ],
  },
  decorators: [
    (story): JSX.Element => (
      <IntlProvider messages={messages[LOCALES.EN_US]} locale={LOCALES.EN_US}>
        <div className="w-[500px]">{story()}</div>
      </IntlProvider>
    ),
  ],
};
