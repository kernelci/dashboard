import { MdOutlineMonitorHeart, MdOutlineDashboard } from "react-icons/md";

import { ImTree, ImImages } from "react-icons/im";

import { FormattedMessage } from "react-intl";

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "../ui/navigation-menu";

import { Separator } from "../ui/separator";

type MenuItems = {
  onClick: () => void;
  idIntl: string;
  icon: JSX.Element;
  selected: boolean;
};

const emptyFunc = () : void => {} 

const items: MenuItems[] = [
  {
    onClick: emptyFunc,
    idIntl: "lateralMenu.dashboard",
    icon: <MdOutlineDashboard className="size-5" />,
    selected: false,
  },
  {
    onClick: emptyFunc,
    idIntl: "lateralMenu.treeMonitor",
    icon: <ImTree className="size-5" />,
    selected: true,
  },
  {
    onClick: emptyFunc,
    idIntl: "lateralMenu.deviceMonitor",
    icon: <MdOutlineMonitorHeart className="size-5" />,
    selected: false,
  },
  {
    onClick: emptyFunc,
    idIntl: "lateralMenu.labsMonitor",
    icon: <ImImages className="size-5" />,
    selected: false,
  },
];

const NavLink = ({
  icon,
  idIntl,
}: Pick<MenuItems, "icon" | "idIntl">): JSX.Element => (
  <NavigationMenuLink asChild>
    <a className="flex items-center no-underline hover:text-sky-500">
      <span className="mr-3">{icon}</span>
      <span className="text-sm text-center" ><FormattedMessage  id={idIntl}/> </span>
    </a>
  </NavigationMenuLink>
);

const SideMenu = (): JSX.Element => {
  const selectedItemClassName = "w-full flex pl-5 py-4 cursor-pointer text-sky-500 bg-black border-l-4 border-sky-500";
  const notSelectedItemClassName = "w-full flex pl-5 py-4 cursor-pointer text-white";

  return (
    <NavigationMenu
      className="fixed h-screen justify-start bg-bgSecondary pt-6 flex-col"
      orientation="vertical"
    >
      <div className="w-full px-4">
        <img src="./src/assets/kernelCI_logo.png"className="size-14 text-onSecondary" />
      </div>

      <Separator className="my-4 bg-onSecondary-10" />

      <NavigationMenuList className="flex-col  w-52 space-y-4 space-x-0 ">
        {items.map((item) =>

            <NavigationMenuItem
              className={item.selected ? selectedItemClassName : notSelectedItemClassName}
              key={item.idIntl}
            >
              <NavLink icon={item.icon} idIntl={item.idIntl} />
            </NavigationMenuItem>
          
        )}
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default SideMenu;
