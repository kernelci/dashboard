import { useMemo, type JSX } from 'react';

import { useLocation } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from '@/components/ui/navigation-menu';

import { Separator } from '@/components/ui/separator';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { ExternalLinkIcon } from '@/components/Icons/ExternalLink';

import SendFeedback from './SendFeedback';
import NavLink from './NavLink';
import {
  routeItems,
  linkItems,
  dashboardItems,
  type RouteMenuItems,
} from './menuItems';

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

type SideMenuContentProps = {
  onLinkClick?: () => void;
  className?: string;
};

const SideMenuContent = ({
  onLinkClick,
  className = '',
}: SideMenuContentProps): JSX.Element => {
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
            onClickElement={onLinkClick}
          />
        </NavigationMenuItem>
      )),
    [onLinkClick],
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
            onClickElement={onLinkClick}
          />
        </NavigationMenuItem>
      )),
    [onLinkClick],
  );

  return (
    <NavigationMenu
      className={`bg-bg-secondary flex-col justify-start pt-6 ${className}`}
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

export default SideMenuContent;
