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
  children?: React.ReactNode;
  onCancel?: () => void;
  onFilter?: () => void;
}

const DrawerHeader = (): JSX.Element => {
  return (
    <header className="mb-7 w-full">
      <div className="w-[1400px] mx-auto flex items-center justify-between mb-4">
        <span className="font-bold text-2xl/[42px]">
          <FormattedMessage id="filter.filtering" />
        </span>
        <DrawerClose asChild>
          <IoClose className="w-6 h-6 cursor-pointer" />
        </DrawerClose>
      </div>
      <Separator />
    </header>
  );
};

const DrawerLink = ({ treeURL }: IDrawerLink): JSX.Element => {
  return (
    <div className="flex justify-between items-center mb-8">
      <div className="w-full h-[52px] px-4 py-2 bg-white border border-darkGray flex flex-col">
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

const Drawer = ({
  treeURL,
  children,
  onCancel,
  onFilter,
}: IFilterDrawer): JSX.Element => {
  return (
    <UIDrawer>
      <DrawerTrigger asChild>
        <Button variant="outline">
          <FormattedMessage id="global.filters" />
        </Button>
      </DrawerTrigger>

      <DrawerContent className="flex items-center px-4 bg-lightGray max-h-screen">
        <DrawerHeader />
        <section className="overflow-y-auto max-h-full">
          <DrawerLink treeURL={treeURL} />
          <div className="w-[1000px] rounded-lg bg-white">
            {React.Children.map(children, (child, idx) => (
              <>
                {idx != 0 && <Separator />}
                <div className="px-6 py-10">{child}</div>
              </>
            ))}
          </div>
        </section>

        <DrawerFooter className="flex flex-row justify-end w-full h-20 bg-white text-dimGray mt-6 gap-x-6">
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
