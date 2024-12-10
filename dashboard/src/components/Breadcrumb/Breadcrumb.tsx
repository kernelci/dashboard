import type { ComponentProps } from 'react';

import { Link } from '@tanstack/react-router';
import type { LinkProps } from '@tanstack/react-router';

import {
  Breadcrumb,
  BreadcrumbList as BreadcrumbListComponent,
  BreadcrumbItem,
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

type BreadcrumbLinkProps = Pick<
  LinkProps,
  'to' | 'params' | 'from' | 'search' | 'children'
>;

const BreadcrumbLink = ({
  children,
  ...props
}: BreadcrumbLinkProps): JSX.Element => {
  return (
    <Link
      {...props}
      className="transition-colors hover:text-slate-500 dark:hover:text-slate-50"
    >
      {children}
    </Link>
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
