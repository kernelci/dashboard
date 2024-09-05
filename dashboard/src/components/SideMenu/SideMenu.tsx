import { MdOutlineMonitorHeart } from 'react-icons/md';

import { ImTree, ImImages } from 'react-icons/im';
import { HiOutlineDocumentSearch } from 'react-icons/hi';

import { useRouter, useSearch } from '@tanstack/react-router';

import { useMemo } from 'react';

import { MessagesKey } from '@/locales/messages';

import { zOrigin } from '@/types/tree/Tree';

import { DOCUMENTATION_URL } from '@/utils/constants/general';

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from '../ui/navigation-menu';

import { Separator } from '../ui/separator';

import SendFeedback from './SendFeedback';

import NavLink from './NavLink';

type RouteMenuItems = {
  onClick: () => void;
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

const emptyFunc = (): void => {};

const SideMenu = (): JSX.Element => {
  const selectedItemClassName =
    'w-full flex pl-5 py-4 cursor-pointer text-sky-500 bg-black border-l-4 border-sky-500';
  const notSelectedItemClassName =
    'w-full flex pl-5 py-4 cursor-pointer text-white';

  const useNavigateTo = (path: string): (() => void) => {
    const router = useRouter();
    const { origin: unsafeOrigin } = useSearch({ strict: false });
    const origin = zOrigin.parse(unsafeOrigin);

    let finalPath = path;
    if (!finalPath.endsWith('/')) {
      finalPath = finalPath + '/';
    }

    return () => {
      const newPath = `${finalPath}?origin=${origin}`;
      router.navigate({
        to: newPath,
      });
    };
  };

  const routeItems: RouteMenuItems[] = [
    {
      onClick: useNavigateTo('/'),
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

  const linksItemElements = useMemo(
    () =>
      linkItems.map(item => (
        <NavigationMenuItem
          className={notSelectedItemClassName}
          key={item.idIntl}
        >
          <NavLink
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
          <NavigationMenuItem
            className={
              item.selected ? selectedItemClassName : notSelectedItemClassName
            }
            key={item.idIntl}
            onClick={item.onClick}
          >
            <NavLink icon={item.icon} idIntl={item.idIntl} />
          </NavigationMenuItem>
        ))}
        <Separator className="my-4 bg-onSecondary-10" />
        {linksItemElements}
        <SendFeedback className={notSelectedItemClassName} />
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default SideMenu;
