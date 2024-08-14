import type { StoryObj, Meta } from '@storybook/react';

import Select, { SelectItem } from './Select';

export default {
  title: 'Components/Select',
  component: Select,
} satisfies Meta<typeof Select>;

type Story = StoryObj<typeof Select>;

export const Default: Story = {
  args: {},
  render: function Render() {
    return (
      <Select>
        <SelectItem value="light">Light</SelectItem>
        <SelectItem value="dark">Dark</SelectItem>
        <SelectItem value="system">System</SelectItem>
      </Select>
    );
  },
};
