import type { StoryObj, Meta } from '@storybook/react';

import {
  Breadcrumb as BreadcrumbComponent,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
} from './Breadcrumb';

export default {
  title: 'Components/Breadcrumb',
  component: BreadcrumbComponent,
} satisfies Meta<typeof BreadcrumbComponent>;

type Story = StoryObj<typeof BreadcrumbComponent>;

export const Default: Story = {
  args: {},
  render: function Render(args) {
    return (
      <BreadcrumbComponent {...args}>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="#">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbEllipsis />
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink href="#">Page</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Current Page</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </BreadcrumbComponent>
    );
  },
};
