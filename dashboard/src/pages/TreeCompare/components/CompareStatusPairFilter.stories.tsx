import type { JSX } from 'react';
import { useState } from 'react';

import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from '@storybook/test';
import { IntlProvider } from 'react-intl';

import { LOCALES } from '@/locales/constants';
import { messages } from '@/locales/messages';

import { TooltipProvider } from '@/components/Tooltip';

import {
  CompareStatusPairChip,
  CompareStatusPairFilter,
  CompareStatusSelect,
  type CompareStatusPair,
} from './CompareStatusPairFilter';

const DEFAULT_PAIRS: CompareStatusPair[] = [
  { from: 'PASS', to: 'FAIL' },
  { from: 'FAIL', to: 'PASS' },
];

const meta: Meta<typeof CompareStatusPairFilter> = {
  title: 'Tree Compare/Status Pair Filter',
  component: CompareStatusPairFilter,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <IntlProvider messages={messages[LOCALES.EN_US]} locale={LOCALES.EN_US}>
        <TooltipProvider>
          <div className="w-[min(40rem,90vw)]">
            <Story />
          </div>
        </TooltipProvider>
      </IntlProvider>
    ),
  ],
  args: {
    value: DEFAULT_PAIRS,
    onChange: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

function StatefulFilter({
  initialValue,
  onChange,
}: {
  initialValue: CompareStatusPair[];
  onChange: (value: CompareStatusPair[]) => void;
}): JSX.Element {
  const [value, setValue] = useState(initialValue);

  return (
    <CompareStatusPairFilter
      value={value}
      onChange={nextValue => {
        setValue(nextValue);
        onChange(nextValue);
      }}
    />
  );
}

export const Default: Story = {
  render: args => (
    <StatefulFilter initialValue={[...args.value]} onChange={args.onChange} />
  ),
};

export const Empty: Story = {
  args: {
    value: [],
  },
  render: args => <StatefulFilter initialValue={[]} onChange={args.onChange} />,
};

export const DuplicateGuard: Story = {
  render: args => (
    <StatefulFilter initialValue={[...args.value]} onChange={args.onChange} />
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const page = within(document.body);

    await userEvent.click(canvas.getByRole('combobox', { name: 'From' }));
    await userEvent.click(page.getByRole('option', { name: 'PASS' }));
    await userEvent.click(canvas.getByRole('combobox', { name: 'To' }));
    await userEvent.click(page.getByRole('option', { name: 'FAIL' }));

    const addButton = canvas.getByRole('button', { name: 'Add' });
    await expect(addButton).toBeDisabled();

    await userEvent.click(
      canvas.getByRole('button', { name: 'Remove PASS to FAIL filter' }),
    );
    await expect(addButton).toBeEnabled();

    await userEvent.click(addButton);
    await expect(
      canvas.getByRole('button', { name: 'Remove PASS to FAIL filter' }),
    ).toBeInTheDocument();
    await expect(addButton).toBeDisabled();
    await expect(
      canvas.getByRole('combobox', { name: 'From' }),
    ).toHaveTextContent('Select status');
    await expect(
      canvas.getByRole('combobox', { name: 'To' }),
    ).toHaveTextContent('Select status');
  },
};

export const StatusSelect: Story = {
  render: function Render() {
    const [value, setValue] = useState<CompareStatusPair['from']>();
    return (
      <CompareStatusSelect
        id="status-select-story"
        label="From"
        value={value}
        onChange={setValue}
      />
    );
  },
};

export const StatusPairChip: Story = {
  render: args => (
    <CompareStatusPairChip
      pair={{ from: 'PASS', to: 'FAIL' }}
      onRemove={() => args.onChange([])}
    />
  ),
};
