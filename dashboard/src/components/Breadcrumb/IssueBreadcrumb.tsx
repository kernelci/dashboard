import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';

import { memo, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from './Breadcrumb';

const IssueBreadcrumb = ({
  searchParams,
  locationMessage,
}: {
  searchParams: LinkProps['search'];
  locationMessage: MessageDescriptor['id'];
}): JSX.Element => {
  return (
    <Breadcrumb className="pt-6 pb-6">
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink to="/issues" search={searchParams}>
            <FormattedMessage id="issue.path" />
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>
            <FormattedMessage id={locationMessage} />
          </BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  );
};
export const MemoizedIssueBreadcrumb = memo(IssueBreadcrumb);
