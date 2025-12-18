import { useMemo, type JSX } from 'react';

import { MdOutlineMonitorHeart } from 'react-icons/md';

import { RxRadiobutton } from 'react-icons/rx';

import { ImTree } from 'react-icons/im';
import { HiOutlineDocumentSearch } from 'react-icons/hi';

import { useLocation } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';

import { DOCUMENTATION_URL } from '@/utils/constants/general';

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from '@/components/ui/navigation-menu';

import { Separator } from '@/components/ui/separator';

import type { PossibleMonitorPath } from '@/types/general';

import { ExternalLinkIcon } from '@/components/Icons/ExternalLink';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import SendFeedback from './SendFeedback';

import NavLink from './NavLink';

type RouteMenuItems = {
  navigateTo: PossibleMonitorPath;
  idIntl: MessagesKey;
  icon: JSX.Element;
  selected: boolean;
};

type LinkMenuItems = {
  url: string;
  idIntl: MessagesKey;
  icon: JSX.Element;
};

type LinkStringItems = {
  url: string;
  label: string;
};

const linkItems: LinkMenuItems[] = [
  {
    url: DOCUMENTATION_URL,
    idIntl: 'global.documentation',
    icon: <HiOutlineDocumentSearch />,
  },
];

const dashboardItems: LinkStringItems[] = [
  {
    url: 'https://kdevops.org/',
    label: 'kdevops',
  },
  {
    url: 'https://netdev.bots.linux.dev/contest.html',
    label: 'netdev-CI',
  },
];

type SideMenuItemProps = {
  item: RouteMenuItems;
};

const SideMenuItem = ({ item }: SideMenuItemProps): JSX.Element => {
  const { pathname } = useLocation();

  const isCurrentPath =
    pathname.startsWith(item.navigateTo) &&
    (pathname.length === item.navigateTo.length ||
      pathname[item.navigateTo.length] === '/');

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
    {
      navigateTo: '/hardware-new',
      idIntl: 'routes.hardwareNewMonitor',
      icon: <MdOutlineMonitorHeart className="size-5" />,
      selected: false,
    },
    {
      navigateTo: '/issues',
      idIntl: 'routes.issueMonitor',
      icon: <RxRadiobutton className="size-5" />,
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

  const dashboardElements = useMemo(
    () =>
      dashboardItems.map(item => (
        <NavigationMenuItem key={item.label} className="w-full">
          <NavLink
            asTag="a"
            icon={<ExternalLinkIcon />}
            label={item.label}
            href={item.url}
            target="_blank"
          />
        </NavigationMenuItem>
      )),
    [],
  );

  return (
    <NavigationMenu
      className="bg-bg-secondary min-h-screen flex-col justify-start pt-6"
      orientation="vertical"
    >
      <div className="w-full px-4">
        <img src="/kernelci-logo-white.svg" className="max-w-[125px]" />
      </div>

      <Separator className="bg-on-secondary-10 my-4" />

      <NavigationMenuList className="w-56 flex-col space-y-4 space-x-0">
        {routeItems.map(item => (
          <SideMenuItem item={item} key={item.idIntl} />
        ))}
        <Separator className="bg-on-secondary-10 my-4" />
        {linksItemElements}
        <SendFeedback className="w-full" />
        <Separator className="bg-on-secondary-10 my-4" />
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-2 text-white">
              <FormattedMessage id={'sidemenu.communityDashboards'} />
            </div>
          </TooltipTrigger>
          <TooltipContent className="max-w-[450px]">
            <FormattedMessage id={'sidemenu.communityDashboardsMsg'} />
          </TooltipContent>
        </Tooltip>
        <div className="flex w-full flex-col space-y-0">
          {dashboardElements}
        </div>
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default SideMenu;
