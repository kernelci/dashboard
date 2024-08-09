import React from 'react';
import { FormattedMessage } from 'react-intl';

import { IoClose } from 'react-icons/io5';

import { Button } from '../ui/button';

import {
  Drawer as UIDrawer,
  DrawerContent,
  DrawerFooter,
  DrawerClose,
  DrawerTrigger,
} from '../ui/drawer';
import { Separator } from '../ui/separator';

interface IDrawerLink {
  treeURL: string;
}

interface IFilterDrawer extends IDrawerLink {
  onOpenChange?: (open: boolean) => void;
  children?: React.ReactNode;
  onCancel?: () => void;
  onFilter?: () => void;
}

const DrawerHeader = (): JSX.Element => {
  return (
    <header className="mb-7 w-full">
      <div className="mx-auto mb-4 flex w-[1400px] items-center justify-between">
        <span className="text-2xl/[42px] font-bold">
          <FormattedMessage id="filter.filtering" />
        </span>
        <DrawerClose asChild>
          <IoClose className="h-6 w-6 cursor-pointer" />
        </DrawerClose>
      </div>
      <Separator />
    </header>
  );
};

const DrawerLink = ({ treeURL }: IDrawerLink): JSX.Element => {
  return (
    <div className="mb-8 flex items-center justify-between">
      <div className="flex h-[52px] w-full flex-col border border-darkGray bg-white px-4 py-2">
        <span className="text-xs text-darkGray2">
          <FormattedMessage id="filter.treeURL" />
        </span>
        <a
          className="text-base text-dimBlack underline"
          href={treeURL}
          target="_bank"
        >
          {treeURL}
        </a>
      </div>
    </div>
  );
};

export const DrawerSection = ({
  children,
  hideSeparator = false,
}: {
  children: React.ReactNode;
  hideSeparator?: boolean;
}): JSX.Element => {
  return (
    <>
      {!hideSeparator && <Separator />}
      <div className="px-6 py-10">{children}</div>
    </>
  );
};

const Drawer = ({
  treeURL,
  children,
  onCancel,
  onFilter,
  onOpenChange,
}: IFilterDrawer): JSX.Element => {
  return (
    <UIDrawer onOpenChange={onOpenChange}>
      <DrawerTrigger asChild>
        <Button variant="outline">
          <FormattedMessage id="global.filters" />
        </Button>
      </DrawerTrigger>

      <DrawerContent className="flex max-h-screen items-center bg-lightGray px-4">
        <DrawerHeader />
        <section className="max-h-full overflow-y-auto">
          <DrawerLink treeURL={treeURL} />
          <div className="w-[1000px] rounded-lg bg-white">
            {React.Children.map(children, child => (
              <>{child}</>
            ))}
          </div>
        </section>

        <DrawerFooter className="mt-6 flex h-20 w-full flex-row justify-end gap-x-6 bg-white text-dimGray">
          <DrawerClose asChild>
            <Button variant="ghost" onClick={onCancel}>
              Cancel
            </Button>
          </DrawerClose>
          <DrawerClose
            asChild
            className="w-[200px] rounded-full bg-lightBlue text-white"
          >
            <Button variant="outline" onClick={onFilter}>
              Filter
            </Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </UIDrawer>
  );
};

export default Drawer;
