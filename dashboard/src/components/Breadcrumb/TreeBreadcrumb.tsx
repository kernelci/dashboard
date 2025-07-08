import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';

import { memo, useMemo, type JSX } from 'react';

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
  const {
    treeName,
    branch,
    id: treeId,
  } = useRouterState({
    select: s => s.location.state,
  });
  const canGoDirect = treeName && branch && treeId;

  const treeParams = useMemo(
    () =>
      canGoDirect
        ? ({
            to: '/tree/$treeName/$branch/$hash',
            params: { treeName: treeName, branch: branch, hash: treeId },
          } as const)
        : ({ to: '/tree/$treeId', params: { treeId: treeId } } as const),
    [canGoDirect, treeName, branch, treeId],
  );

  const breadcrumbLink = useMemo(
    () => (
      <BreadcrumbLink
        to={treeParams.to}
        params={treeParams.params}
        search={searchParams}
        state={s => s}
      >
        <FormattedMessage id="tree.details" />
      </BreadcrumbLink>
    ),
    [treeParams, searchParams],
  );

  return (
    <Breadcrumb className="pt-6 pb-6">
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink to="/tree" search={searchParams}>
            <FormattedMessage id="tree.path" />
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        {breadcrumbLink}
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
