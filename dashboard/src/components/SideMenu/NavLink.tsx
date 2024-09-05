import { FormattedMessage } from 'react-intl';

import { AnchorHTMLAttributes } from 'react';

import { MessagesKey } from '@/locales/messages';

import { NavigationMenuLink } from '../ui/navigation-menu';

interface INavLink extends AnchorHTMLAttributes<HTMLAnchorElement> {
  idIntl: MessagesKey;
  icon: JSX.Element;
}

const NavLink = ({ icon, idIntl, ...props }: INavLink): JSX.Element => (
  <NavigationMenuLink asChild>
    <a className="flex items-center no-underline hover:text-sky-500" {...props}>
      <span className="mr-3">{icon}</span>
      <span className="text-center text-sm">
        <FormattedMessage id={idIntl} />{' '}
      </span>
    </a>
  </NavigationMenuLink>
);

export default NavLink;
