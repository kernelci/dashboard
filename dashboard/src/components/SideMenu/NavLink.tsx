import { FormattedMessage } from 'react-intl';

import { Link, LinkProps } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import { NavigationMenuLink } from '../ui/navigation-menu';

type INavLink = LinkProps & {
  idIntl: MessagesKey;
  icon: JSX.Element;
  href?: string;
};

const NavLink = ({ icon, idIntl, ...props }: INavLink): JSX.Element => {
  return (
    <NavigationMenuLink asChild>
      <Link
        className="flex items-center no-underline hover:text-sky-500"
        {...props}
      >
        <span className="mr-3">{icon}</span>
        <span className="text-center text-sm">
          <FormattedMessage id={idIntl} />{' '}
        </span>
      </Link>
    </NavigationMenuLink>
  );
};

export default NavLink;
