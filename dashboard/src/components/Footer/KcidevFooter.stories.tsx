import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from '@storybook/test';
import { IntlProvider } from 'react-intl';

import type { JSX } from 'react';

import { LOCALES } from '@/locales/constants';
import { messages } from '@/locales/messages';

import { MemoizedKcidevFooter } from './KcidevFooter';

const completeCommand =
  "kci-dev results trees --origin 'unsafe origin' --days 7";

const meta: Meta<typeof MemoizedKcidevFooter> = {
  title: 'Components/Footer/KcidevFooter',
  component: MemoizedKcidevFooter,
  decorators: [
    (story): JSX.Element => (
      <IntlProvider messages={messages[LOCALES.EN_US]} locale={LOCALES.EN_US}>
        {story()}
      </IntlProvider>
    ),
  ],
  args: {
    command: {
      id: 'trees',
      label: 'Tree listing',
      argv: [
        'kci-dev',
        'results',
        'trees',
        '--origin',
        'unsafe origin',
        '--days',
        '7',
      ],
      omittedFilters: ['tree search'],
      reproduction: 'partial',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Interaction: Story = {
  play: async ({ canvasElement, step }) => {
    const canvas = within(canvasElement);
    const page = within(canvasElement.ownerDocument.body);
    const writeText = fn<Clipboard['writeText']>().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    });
    const trigger = canvas.getByRole('button', { name: 'CLI command' });

    await step(
      'opens by keyboard and exposes the complete command',
      async () => {
        trigger.focus();
        await userEvent.keyboard('{Enter}');
        await expect(
          page.getByRole('heading', { name: 'Run this query with kci-dev' }),
        ).toBeVisible();
        await expect(
          page.getByLabelText('Tree listing: Human-readable'),
        ).toHaveTextContent(completeCommand);
        await expect(page.getByRole('note')).toHaveTextContent('tree search');
      },
    );

    await step(
      'reports copy success only after the clipboard resolves',
      async () => {
        await userEvent.click(
          page.getByRole('button', { name: 'Copy command: Human-readable' }),
        );
        await expect(writeText).toHaveBeenCalledWith(completeCommand);
        await expect(page.getByText('Copied')).toBeVisible();
      },
    );

    await step('Escape closes the popover and returns focus', async () => {
      await userEvent.keyboard('{Escape}');
      await expect(trigger).toHaveFocus();
    });

    await step(
      'keeps the command selectable and reports clipboard errors',
      async () => {
        writeText.mockRejectedValueOnce(new Error('Clipboard denied'));
        await userEvent.keyboard('{Enter}');
        await userEvent.click(
          page.getByRole('button', { name: 'Copy command: Human-readable' }),
        );
        await expect(page.getByRole('alert')).toHaveTextContent(
          'Select it above and copy it manually.',
        );
        await expect(
          page.getByLabelText('Tree listing: Human-readable'),
        ).toHaveTextContent(completeCommand);
      },
    );
  },
};
