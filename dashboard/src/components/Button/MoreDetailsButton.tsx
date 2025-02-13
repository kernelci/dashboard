import { FormattedMessage } from 'react-intl';

import { memo, type JSX } from 'react';

import { Link, type LinkProps } from '@tanstack/react-router';

import { Button } from '@/components/ui/button';
import { MoreDetailsIcon } from '@/components/Table/DetailsColumn';

const MoreDetailsLinkButton = ({
  linkProps,
}: {
  linkProps: LinkProps;
}): JSX.Element => {
  return (
    <Button
      asChild
      variant="outline"
      className="text-dim-gray hover:bg-medium-gray w-min rounded-full border-2 border-black text-sm"
    >
      <Link {...linkProps}>
        <div className="flex gap-2">
          <FormattedMessage id="global.showMoreDetails" />
          <MoreDetailsIcon />
        </div>
      </Link>
    </Button>
  );
};
export const MemoizedMoreDetailsButton = memo(MoreDetailsLinkButton);

const MoreDetailsIconLink = ({
  linkProps,
}: {
  linkProps: LinkProps;
}): JSX.Element => {
  return (
    <Link {...linkProps}>
      <MoreDetailsIcon />
    </Link>
  );
};
export const MemoizedMoreDetailsIconLink = memo(MoreDetailsIconLink);
