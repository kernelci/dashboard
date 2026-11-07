import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';

import { memo, useMemo, type JSX } from 'react';

import type { HistoryState, LinkProps } from '@tanstack/react-router';
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
  tree,
}: {
  searchParams: LinkProps['search'];
  locationMessage: MessageDescriptor['id'];
  tree?: Pick<HistoryState, 'treeName' | 'branch' | 'id'>;
}): JSX.Element => {
  const historyState = useRouterState({
    select: s => s.location.state,
  });
  const { treeName, branch, id: treeId } = tree ?? historyState;
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
    () =>
      treeId ? (
        <BreadcrumbLink
          to={treeParams.to}
          params={treeParams.params}
          search={searchParams}
          state={s => (tree ? {} : s)}
        >
          <FormattedMessage id="tree.details" />
        </BreadcrumbLink>
      ) : (
        <span>
          <FormattedMessage id="tree.details" />
        </span>
      ),
    [treeId, treeParams, searchParams, tree],
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
        <BreadcrumbItem>{breadcrumbLink}</BreadcrumbItem>
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
