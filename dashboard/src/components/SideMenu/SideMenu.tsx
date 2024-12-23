import { useMemo } from 'react';

import { MdOutlineMonitorHeart } from 'react-icons/md';

import { ImTree } from 'react-icons/im';
import { HiOutlineDocumentSearch } from 'react-icons/hi';

import { useLocation } from '@tanstack/react-router';

import type { MessagesKey } from '@/locales/messages';

import { DOCUMENTATION_URL } from '@/utils/constants/general';

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from '@/components/ui/navigation-menu';

import { Separator } from '@/components/ui/separator';

import SendFeedback from './SendFeedback';

import NavLink from './NavLink';

type RouteMenuItems = {
  navigateTo: '/tree' | '/hardware';
  idIntl: MessagesKey;
  icon: JSX.Element;
  selected: boolean;
};

type LinkMenuItems = {
  url: string;
  idIntl: MessagesKey;
  icon: JSX.Element;
};

const linkItems: LinkMenuItems[] = [
  {
    url: DOCUMENTATION_URL,
    idIntl: 'global.documentation',
    icon: <HiOutlineDocumentSearch />,
  },
];

type SideMenuItemProps = {
  item: RouteMenuItems;
};

const SideMenuItem = ({ item }: SideMenuItemProps): JSX.Element => {
  const { pathname } = useLocation();

  const isCurrentPath = pathname.startsWith(item.navigateTo);

  return (
    <NavigationMenuItem key={item.idIntl} className="w-full">
      <NavLink
        selected={isCurrentPath}
        to={item.navigateTo}
        search={prevSearch => ({
          origin: prevSearch.origin,
        })}
        icon={item.icon}
        idIntl={item.idIntl}
      />
    </NavigationMenuItem>
  );
};

const SideMenu = (): JSX.Element => {
  const routeItems: RouteMenuItems[] = [
    {
      navigateTo: '/tree',
      idIntl: 'routes.treeMonitor',
      icon: <ImTree className="size-5" />,
      selected: true,
    },
    {
      navigateTo: '/hardware',
      idIntl: 'routes.hardwareMonitor',
      icon: <MdOutlineMonitorHeart className="size-5" />,
      selected: false,
    },
  ];

  const linksItemElements = useMemo(
    () =>
      linkItems.map(item => (
        <NavigationMenuItem key={item.idIntl} className="w-full">
          <NavLink
            asTag="a"
            icon={item.icon}
            idIntl={item.idIntl}
            href={item.url}
            target="_blank"
          />
        </NavigationMenuItem>
      )),
    [],
  );

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
        {routeItems.map(item => (
          <SideMenuItem item={item} key={item.idIntl}></SideMenuItem>
        ))}
        <Separator className="my-4 bg-onSecondary-10" />
        {linksItemElements}
        <SendFeedback className="w-full" />
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default SideMenu;
