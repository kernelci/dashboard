import type { Meta, StoryObj } from '@storybook/react';
import { IntlProvider } from 'react-intl';
import { flatten } from 'flat';

import { fn } from '@storybook/test';

import { LOCALES } from '../../../locales/constants';

import { messages } from '../../../locales/messages';

import TimeRangeSection from '../TimeRangeSection';

const ActionsData = {
  onMinChange: fn(),
  onMaxChange: fn(),
};

const meta: Meta<typeof TimeRangeSection> = {
  title: 'Filter TimeRangeSection',
  component: TimeRangeSection,
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
    title: 'Timing',
    subtitle: 'Please select a range of timing:',
    min: 0,
    max: 10,
  },
  decorators: [
    (story): JSX.Element => (
      <IntlProvider
        messages={flatten(messages[LOCALES.EN_US])}
        locale={LOCALES.EN_US}
      >
        <div className="w-[500px]">{story()}</div>
      </IntlProvider>
    ),
  ],
};
