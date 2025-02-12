import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';

import { memo } from 'react';

import type { LinkProps } from '@tanstack/react-router';
import { useRouterState } from '@tanstack/react-router';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from './Breadcrumb';

const HardwareBreadcrumb = ({
  searchParams,
  locationMessage,
}: {
  searchParams: LinkProps['search'];
  locationMessage: MessageDescriptor['id'];
}): JSX.Element => {
  const hardwareId = useRouterState({ select: s => s.location.state.id });
  return (
    <Breadcrumb className="pt-6 pb-6">
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink to="/hardware" search={searchParams}>
            <FormattedMessage id="hardware.path" />
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbLink
          to="/hardware/$hardwareId"
          params={{ hardwareId }}
          search={searchParams}
          state={s => s}
        >
          <FormattedMessage id="hardware.details" />
        </BreadcrumbLink>
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
export const MemoizedHardwareBreadcrumb = memo(HardwareBreadcrumb);
