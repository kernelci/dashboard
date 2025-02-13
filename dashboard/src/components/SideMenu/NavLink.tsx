import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import type { JSX } from 'react';

import type { MessagesKey } from '@/locales/messages';

import { NavigationMenuLink } from '../ui/navigation-menu';

type INavLink = LinkProps & {
  idIntl: MessagesKey;
  icon: JSX.Element;
  href?: string;
  asTag?: string;
  selected?: boolean;
};

const NavLink = ({
  selected = false,
  icon,
  idIntl,
  asTag,
  ...props
}: INavLink): JSX.Element => {
  const LinkElement = asTag ?? Link;

  const baseClassName =
    'items-center hover:text-sky-500 w-full flex pl-5 py-4 cursor-pointer';

  const selectedItemClassName =
    'text-sky-500 bg-black border-l-4 border-sky-500';

  const notSelectedItemClassName = 'text-white';

  return (
    <NavigationMenuLink asChild>
      <LinkElement
        className={`${baseClassName} ${selected ? selectedItemClassName : notSelectedItemClassName}`}
        {...props}
      >
        <span className="mr-3">{icon}</span>
        <span className="text-center text-sm">
          <FormattedMessage id={idIntl} />
        </span>
      </LinkElement>
    </NavigationMenuLink>
  );
};

export default NavLink;
