import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import type { JSX } from 'react';

import type { MessagesKey } from '@/locales/messages';

import { cn } from '@/lib/utils';

import { NavigationMenuLink } from '../ui/navigation-menu';

type INavLinkBase = LinkProps & {
  icon?: JSX.Element;
  href?: string;
  asTag?: string;
  selected?: boolean;
  linkClassName?: string;
  onClickElement?: () => void;
};

type INavLinkWithIntl = INavLinkBase & {
  idIntl: MessagesKey;
  label?: never;
};

type INavLinkWithLabel = INavLinkBase & {
  idIntl?: never;
  label: string;
};

type INavLink = INavLinkWithIntl | INavLinkWithLabel;

const NavLink = ({
  selected = false,
  icon,
  idIntl,
  label,
  asTag,
  linkClassName,
  onClickElement,
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
        className={cn(
          baseClassName,
          selected ? selectedItemClassName : notSelectedItemClassName,
          linkClassName,
        )}
        onClick={onClickElement}
        {...props}
      >
        {icon && <span className="mr-3">{icon}</span>}
        <span className="text-center text-sm">
          {label ?? <FormattedMessage id={idIntl} />}
        </span>
      </LinkElement>
    </NavigationMenuLink>
  );
};

export default NavLink;
