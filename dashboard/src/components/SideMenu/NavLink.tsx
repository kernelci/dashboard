import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';

import type { MessagesKey } from '@/locales/messages';

import { NavigationMenuLink } from '../ui/navigation-menu';

type INavLink = LinkProps & {
  idIntl: MessagesKey;
  icon: JSX.Element;
  href?: string;
  asTag?: string;
};

const NavLink = ({ icon, idIntl, asTag, ...props }: INavLink): JSX.Element => {
  const LinkElement = asTag ?? Link;

  return (
    <NavigationMenuLink asChild>
      <LinkElement
        className="flex items-center no-underline hover:text-sky-500"
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
