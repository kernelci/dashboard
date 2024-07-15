import type { Meta, StoryObj } from '@storybook/react';

import Accordion, { IAccordionItems } from './Accordion';

const meta = {
  title: 'Accordion',
  component: Accordion,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Accordion>;

export default meta;
type Story = StoryObj<typeof meta>;

const itemsBuild: IAccordionItems[] = [
  {
    trigger: {
      config: 'config',
      compiler: 'compiler',
      date: 'dd/mm/yyyy',
      buildErrors: 5,
      buildTime: '500 seconds',
      status: 'valid',
    },
    content: <span>AAAAa</span>,
  },
  {
    trigger: {
      config: 'config',
      compiler: 'compiler',
      date: 'dd/mm/yyyy',
      buildErrors: 5,
      buildTime: '500 seconds',
      status: 'valid',
    },
    content: <span>AAAAa</span>,
  },
  {
    trigger: {
      config: 'config',
      compiler: 'compiler',
      date: 'dd/mm/yyyy',
      buildErrors: 5,
      buildTime: '500 seconds',
      status: 'valid',
    },
    content: <span>AAAAa</span>,
  },
];

const headersBuild = [
  'config',
  'compiler',
  'date',
  'build errors',
  'build time',
  'status',
];

const itemsTest: IAccordionItems[] = [
  {
    trigger: {
      testPlans: 'aaaaaaa',
      testErrors: 5,
      testSuccessfull: 12,
      status: 'invalid',
    },
    content: <span>AAAAa</span>,
  },
  {
    trigger: {
      testPlans: 'aaaaaaasdkjmla',
      testErrors: 5,
      testSuccessfull: 12,
      status: 'valid',
    },
    content: <span>BBB</span>,
  },
];
const headersTest = ['test plan', 'test results', 'status'];

export const Builds: Story = {
  args: {
    items: itemsBuild,
    headers: headersBuild,
    type: 'build',
  },
};

export const Tests: Story = {
  args: {
    items: itemsTest,
    headers: headersTest,
    type: 'test',
  },
};
