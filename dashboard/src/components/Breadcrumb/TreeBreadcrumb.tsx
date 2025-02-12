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

const TreeBreadcrumb = ({
  searchParams,
  locationMessage,
}: {
  searchParams: LinkProps['search'];
  locationMessage: MessageDescriptor['id'];
}): JSX.Element => {
  const treeId = useRouterState({ select: s => s.location.state.id });
  return (
    <Breadcrumb className="pt-6 pb-6">
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink to="/tree" search={searchParams}>
            <FormattedMessage id="tree.path" />
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbLink
          to={`/tree/$treeId`}
          params={{ treeId: treeId }}
          search={searchParams}
          state={s => s}
        >
          <FormattedMessage id="tree.details" />
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
export const MemoizedTreeBreadcrumb = memo(TreeBreadcrumb);
