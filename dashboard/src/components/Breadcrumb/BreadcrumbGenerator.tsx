import { Fragment, memo, type JSX } from 'react';
import { FormattedMessage } from 'react-intl';
import type { LinkProps } from '@tanstack/react-router';

import type { MessagesKey } from '@/locales/messages';

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from './Breadcrumb';

export interface IBreadcrumbComponent {
  linkProps: LinkProps;
  messageId: MessagesKey;
}

interface IBreadcrumb {
  components: IBreadcrumbComponent[];
}

type BreadcrumbBaseRoute = { path: LinkProps['to']; messageId: MessagesKey };
type BreadcrumbDetailsRoute = BreadcrumbBaseRoute & { paramKey: string };

type BreadcrumbRouteValues = {
  base: BreadcrumbBaseRoute;
  details: BreadcrumbDetailsRoute;
  build: BreadcrumbBaseRoute;
  test: BreadcrumbBaseRoute;
};

type BreadcrumbRouteKeys = 'tree' | 'hardware';

export type BreadcrumbRoute = Record<
  BreadcrumbRouteKeys,
  BreadcrumbRouteValues
>;

const BreadcrumbGenerator = ({ components }: IBreadcrumb): JSX.Element => {
  return (
    <Breadcrumb className="pt-6 pb-6">
      <BreadcrumbList>
        {components.map((component, idx) => {
          return (
            <Fragment key={idx}>
              <BreadcrumbItem>
                <BreadcrumbLink {...component.linkProps}>
                  <FormattedMessage id={component.messageId} />
                </BreadcrumbLink>
              </BreadcrumbItem>
              {components.length - 1 !== idx && <BreadcrumbSeparator />}
            </Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

export const MemoizedBreadcrumbGenerator = memo(BreadcrumbGenerator);
