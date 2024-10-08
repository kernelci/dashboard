import { FormattedMessage } from 'react-intl';

import { Link, LinkProps } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import { NavigationMenuLink } from '../ui/navigation-menu';

/*interface INavLink extends AnchorHTMLAttributes<HTMLAnchorElement> {
  idIntl: MessagesKey;
  icon: JSX.Element;
  to?: string;
}*/

type INavLink = LinkProps & {
  idIntl: MessagesKey;
  icon: JSX.Element;
  href?: string;
  as?: string;
};

const NavLink = ({ icon, idIntl, as, ...props }: INavLink): JSX.Element => {
  const LinkElement = as || Link;

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
