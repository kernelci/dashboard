import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import { IntlProvider } from 'react-intl';
import { flatten } from 'flat';

import { LOCALES } from '../../../locales/constants';

import { messages } from '../../../locales/messages';

import FilterDrawer from '../Drawer';

import CheckboxSection from '../CheckboxSection';
import TimeRangeSection from '../TimeRangeSection';
import SummarySection from '../SummarySection';

const ActionsData = {
  onRefresh: fn(),
  onCancel: fn(),
  onFilter: fn(),
};

const meta: Meta<typeof FilterDrawer> = {
  title: 'FilterDrawer',
  component: FilterDrawer,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  decorators: [
    (): JSX.Element => (
      <IntlProvider
        messages={flatten(messages[LOCALES.EN_US])}
        locale={LOCALES.EN_US}
      >
        <FilterDrawer
          treeURL="https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git"
          {...ActionsData}
        >
          <SummarySection {...summarySectionProps} />
          <CheckboxSection {...checkboxSectionProps} />
          <CheckboxSection {...checkboxSectionProps} />
          <TimeRangeSection {...timeRangeSectionProps} />
        </FilterDrawer>
      </IntlProvider>
    ),
  ],
};

const summarySectionProps = {
  title: 'Tree',
  columns: [
    { title: 'Tree', value: 'stable-rc' },
    { title: 'Matainer', value: 'Shannon Nelson' },
    {
      title: 'Commit/tag',
      value: '5.15.150-rc1 - 3ab4d9c9e190217ee7e974c70b96795cd2f74611',
    },
  ],
};

const checkboxSectionProps = {
  items: ['linux-5.15.y', 'Status:failed', 'Status: Warnings'],
  title: 'Branch',
  subtitle: 'Please select one or more Branches',
  onClickItem: (idx: number, isChecked: boolean): void =>
    console.log(idx, isChecked),
};

const onChangeM = (e: React.FormEvent<HTMLInputElement>): void =>
  console.log(e.target);
const timeRangeSectionProps = {
  title: 'Timing',
  subtitle: 'Please select a range of timing:',
  min: 0,
  max: 100,
  onMinChange: onChangeM,
  onMaxChange: onChangeM,
};
