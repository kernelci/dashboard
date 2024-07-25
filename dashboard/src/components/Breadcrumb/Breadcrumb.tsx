import { ComponentProps } from 'react';

import {
  Breadcrumb,
  BreadcrumbList as BreadcrumbListComponent,
  BreadcrumbItem,
  BreadcrumbLink as BreadcrumbLinkComponent,
  BreadcrumbPage,
  BreadcrumbSeparator as BreadcrumbSeparatorComponent,
  BreadcrumbEllipsis,
} from '../ui/breadcrumb';

type BreadcrumbListProps = Omit<
  ComponentProps<typeof BreadcrumbListComponent>,
  'className'
>;
const BreadcrumbList = ({ ...props }: BreadcrumbListProps): JSX.Element => {
  return <BreadcrumbListComponent {...props} className="text-black" />;
};

type BreadcrumbLinkProps = Omit<
  ComponentProps<typeof BreadcrumbLinkComponent>,
  'className'
>;
const BreadcrumbLink = ({ ...props }: BreadcrumbLinkProps): JSX.Element => {
  return (
    <BreadcrumbLinkComponent {...props} className="hover:text-slate-500" />
  );
};

type BreadcrumbSeparatorProps = Omit<
  ComponentProps<typeof BreadcrumbSeparatorComponent>,
  'className'
>;
const BreadcrumbSeparator = ({
  ...props
}: BreadcrumbSeparatorProps): JSX.Element => {
  return <BreadcrumbSeparatorComponent {...props} className="text-weakGray" />;
};

export {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
};
