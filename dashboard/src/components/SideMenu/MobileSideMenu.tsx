import type { JSX } from 'react';

import useIntl from 'react-intl/src/components/useIntl';

import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from '@/components/ui/drawer';

import SideMenuContent from './SideMenuContent';

type MobileSideMenuProps = {
  isOpen: boolean;
  onClose: () => void;
};

const MobileSideMenu = ({
  isOpen,
  onClose,
}: MobileSideMenuProps): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <Drawer
      direction="left"
      open={isOpen}
      onOpenChange={open => !open && onClose()}
    >
      {/* Hides the first drawer child which is the drawer handle */}
      <DrawerContent className="bg-bg-secondary fixed inset-y-0 right-auto left-0 mt-0 h-full w-auto overflow-y-auto border-none pb-12 [&>div:first-child]:hidden">
        <DrawerHeader className="sr-only">
          <DrawerTitle>{formatMessage({ id: 'sidemenu.title' })}</DrawerTitle>
          <DrawerDescription>
            {formatMessage({ id: 'sidemenu.description' })}
          </DrawerDescription>
        </DrawerHeader>
        <SideMenuContent onLinkClick={onClose} />
      </DrawerContent>
    </Drawer>
  );
};

export default MobileSideMenu;
