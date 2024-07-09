import type { Meta, StoryObj } from '@storybook/react';

import ListingComponentCard from './ListingComponentCard';

const meta = {
  title: 'ListingComponentCard',
  component: ListingComponentCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof ListingComponentCard>;

export default meta;
type Story = StoryObj<typeof meta>;

const itemsDefault = [
  {
    errors: 1,
    warnings: 888,
    text: 'allmodconfig',
  },
  {
    errors: 1,
    warnings: 1,
    text: 'microdroid_defconfig',
  },
  {
    errors: 2,
    warnings: 3,
    text: 'x86_64_defconfig',
  },
  {
    errors: 1,
    warnings: 2,
    text: 'i386_defconfig',
  },
  {
    errors: 1,
    warnings: 1,
    text: 'rv32_defconfig',
  },
];

const itemsErrors = [
  {
    errors: 8,
    warnings: 0,
    text: 'include/linux/fortify-string.h:57:29: error: ‘__builtin_memcpy’ offset 32 is out of the bounds [0, 0] [-Werror=array-bounds]',
  },
  {
    errors: 2,
    warnings: 0,
    text: 'drivers/net/ethernet/realtek/r8169_main.c:5512:23: error: ‘rtl8169_pm_ops’ undeclared here (not in a function); did you mean ‘rtl8169_poll’?',
  },
  {
    errors: 1,
    warnings: 0,
    text: 'arch/x86/include/asm/string_32.h:150:25: error: ‘__builtin_memcpy’ offset 32 is out of the bounds [0, 0] [-Werror=array-bounds]',
  },
];

const itemsWarnings = [
  {
    errors: 0,
    warnings: 10,
    text: 'cc1: all warnings being treated as errors',
  },
  {
    errors: 0,
    warnings: 6,
    text: 'drivers/of/unittest-data/tests-phandle.dtsi:12.18-22: Warning (node_name_vs_property_name): /testcase-data/duplicate-name: node name and property name conflict',
  },
  {
    errors: 0,
    warnings: 5,
    text: 'WARNING: modpost: vmlinux: memblock_end_of_DRAM: EXPORT_SYMBOL used for init symbol. Remove __init or EXPORT_SYMBOL.',
  },
];

export const Default: Story = {
  args: {
    items: itemsDefault,
    title: 'Configs',
  },
};

export const Warnings: Story = {
  args: {
    items: itemsWarnings,
    title: 'Configs',
  },
};

export const Errors: Story = {
  args: {
    items: itemsErrors,
    title: 'Configs',
  },
};
