import { FormattedMessage } from 'react-intl';

import { MessagesKey } from '@/locales/messages';

import { NavigationMenuLink } from '../ui/navigation-menu';

const NavLink = ({
  icon,
  idIntl,
}: {
  idIntl: MessagesKey;
  icon: JSX.Element;
}): JSX.Element => (
  <NavigationMenuLink asChild>
    <a className="flex items-center no-underline hover:text-sky-500">
      <span className="mr-3">{icon}</span>
      <span className="text-center text-sm">
        <FormattedMessage id={idIntl} />{' '}
      </span>
    </a>
  </NavigationMenuLink>
);

export default NavLink;
