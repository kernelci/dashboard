import { MdOutlineMonitorHeart } from 'react-icons/md';

import { ImTree, ImImages } from 'react-icons/im';

import { FormattedMessage } from 'react-intl';

import { MessagesKey } from '@/locales/messages';

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from '../ui/navigation-menu';

import { Separator } from '../ui/separator';

type MenuItems = {
  onClick: () => void;
  idIntl: MessagesKey;
  icon: JSX.Element;
  selected: boolean;
};

const emptyFunc = (): void => {};

const items: MenuItems[] = [
  {
    onClick: emptyFunc,
    idIntl: 'routes.treeMonitor',
    icon: <ImTree className="size-5" />,
    selected: true,
  },
  {
    onClick: emptyFunc,
    idIntl: 'routes.deviceMonitor',
    icon: <MdOutlineMonitorHeart className="size-5" />,
    selected: false,
  },
  {
    onClick: emptyFunc,
    idIntl: 'routes.labsMonitor',
    icon: <ImImages className="size-5" />,
    selected: false,
  },
];

const NavLink = ({
  icon,
  idIntl,
}: Pick<MenuItems, 'icon' | 'idIntl'>): JSX.Element => (
  <NavigationMenuLink asChild>
    <a className="flex items-center no-underline hover:text-sky-500">
      <span className="mr-3">{icon}</span>
      <span className="text-center text-sm">
        <FormattedMessage id={idIntl} />{' '}
      </span>
    </a>
  </NavigationMenuLink>
);

const SideMenu = (): JSX.Element => {
  const selectedItemClassName =
    'w-full flex pl-5 py-4 cursor-pointer text-sky-500 bg-black border-l-4 border-sky-500';
  const notSelectedItemClassName =
    'w-full flex pl-5 py-4 cursor-pointer text-white';

  return (
    <NavigationMenu
      className="min-h-screen flex-col justify-start bg-bgSecondary pt-6"
      orientation="vertical"
    >
      <div className="w-full px-4">
        <img src="/kernelci-logo-white.svg" className="max-w-[125px]" />
      </div>

      <Separator className="my-4 bg-onSecondary-10" />

      <NavigationMenuList className="w-52 flex-col space-x-0 space-y-4">
        {items.map(item => (
          <NavigationMenuItem
            className={
              item.selected ? selectedItemClassName : notSelectedItemClassName
            }
            key={item.idIntl}
          >
            <NavLink icon={item.icon} idIntl={item.idIntl} />
          </NavigationMenuItem>
        ))}
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default SideMenu;
