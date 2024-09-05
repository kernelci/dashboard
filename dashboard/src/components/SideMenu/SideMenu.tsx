import { MdOutlineMonitorHeart } from 'react-icons/md';

import { ImTree, ImImages } from 'react-icons/im';

import { useRouter, useSearch } from '@tanstack/react-router';

import { MessagesKey } from '@/locales/messages';

import { zOrigin } from '@/types/tree/Tree';

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from '../ui/navigation-menu';

import { Separator } from '../ui/separator';

import NavLink from './NavLink';

type MenuItems = {
  onClick: () => void;
  idIntl: MessagesKey;
  icon: JSX.Element;
  selected: boolean;
};

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

  const items: MenuItems[] = [
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
            onClick={item.onClick}
          >
            <NavLink icon={item.icon} idIntl={item.idIntl} />
          </NavigationMenuItem>
        ))}
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default SideMenu;
