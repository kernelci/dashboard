import type { Meta, StoryObj } from '@storybook/react';

import Summary, { ISummaryItem } from './Summary';

const meta = {
  title: 'Summary',
  component: Summary,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Summary>;

export default meta;
type Story = StoryObj<typeof meta>;

const items: ISummaryItem[] = [
  {
    arch: {
      errors: 4,
      warnings: 1,
      text: 'arm64',
    },
    compilers: [
      'aarch64-linux-gnu-gcc (Debian 10.2.1-6) 10.2.1 20210110',
      'Debian clang version 17.0.6 (++20231208085823+6009708b436...)',
    ],
  },
  {
    arch: {
      errors: 4,
      warnings: 1,
      text: 'arm64',
    },
    compilers: [
      'aarch64-linux-gnu-gcc (Debian 10.2.1-6) 10.2.1 20210110',
      'Debian clang version 17.0.6 (++20231208085823+6009708b436...)',
    ],
  },
  {
    arch: {
      errors: 4,
      warnings: 1,
      text: 'arm64',
    },
    compilers: [
      'aarch64-linux-gnu-gcc (Debian 10.2.1-6) 10.2.1 20210110',
      'Debian clang version 17.0.6 (++20231208085823+6009708b436...)',
    ],
  },
  {
    arch: {
      errors: 4,
      warnings: 1,
      text: 'arm64',
    },
    compilers: [
      'aarch64-linux-gnu-gcc (Debian 10.2.1-6) 10.2.1 20210110',
      'Debian clang version 17.0.6 (++20231208085823+6009708b436++20231208085823+6009708b436++20231208085823+6009708b436++20231208085823+6009708b436)',
    ],
  },
];

export const Default: Story = {
  args: {
    summaryBody: items,
    title: 'Summary',
    summaryHeaders: ['Arch', 'Compiler'],
  },
};
