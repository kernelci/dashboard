import React from 'react';
import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';
import { IoChevronDown, IoClose } from 'react-icons/io5';
import { AiOutlineGlobal } from 'react-icons/ai';
import { CgTab } from 'react-icons/cg';

import { Button } from '@/components/ui/button';

import {
  Drawer as UIDrawer,
  DrawerContent,
  DrawerFooter,
  DrawerClose,
  DrawerTrigger,
  DrawerTitle,
  DrawerDescription,
} from '@/components/ui/drawer';
import { Separator } from '@/components/ui/separator';
import ButtonWithIcon from '@/components/Button/ButtonWithIcon';

import { Tooltip, TooltipContent, TooltipTrigger } from '../Tooltip/Tooltip';

export interface IDrawerLink {
  link: {
    title: MessageDescriptor['id'];
    value: string;
    url?: string;
  };
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
      <DrawerTitle>
        <div className="mx-auto mb-4 flex w-[1400px] items-center justify-between">
          <span className="text-2xl/[42px] font-bold">
            <FormattedMessage id="filter.filtering" />
          </span>
          <DrawerClose asChild>
            <IoClose className="h-6 w-6 cursor-pointer" />
          </DrawerClose>
        </div>
      </DrawerTitle>
      <DrawerDescription />
      <Separator />
    </header>
  );
};

const DrawerLink = ({ link }: IDrawerLink): JSX.Element => {
  return (
    <div className="mb-8 flex items-center justify-between">
      <div className="flex h-[52px] w-full flex-col border border-darkGray bg-white px-4 py-2">
        <span className="text-xs text-darkGray2">
          <FormattedMessage id={link.title} />
        </span>
        <a
          className="text-base text-dimBlack underline"
          href={link.url ?? '#'}
          target={link.url ? '_blank' : undefined}
          rel="noreferrer"
        >
          {link.value}
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
      <div className="[&:last-child]:pt-10 [&:not(:last-child)]:py-10">
        {children}
      </div>
    </>
  );
};

type FilterTypeIconProps = {
  type: 'global' | 'tab';
};

const iconClassName = 'text-[1.2rem] text-blue';

const Icons: Record<FilterTypeIconProps['type'], JSX.Element> = {
  global: <AiOutlineGlobal className={iconClassName} />,
  tab: <CgTab className={iconClassName} />,
};

const iconMessage: Record<
  FilterTypeIconProps['type'],
  MessageDescriptor['id']
> = {
  global: 'filter.globalFilterAllTabs',
  tab: 'filter.onlySpecificTab',
};

export const FilterTypeIcon = ({ type }: FilterTypeIconProps): JSX.Element => {
  return (
    <Tooltip>
      <TooltipTrigger>{Icons[type]}</TooltipTrigger>
      <TooltipContent>
        <FormattedMessage id={iconMessage[type]} />
      </TooltipContent>
    </Tooltip>
  );
};

const Legend = (): JSX.Element => {
  return (
    <div className="flex items-center gap-1 pb-8 pt-6 font-semibold">
      <span className="mr-1">
        <FormattedMessage id="global.legend" />
      </span>
      <span className="flex items-center gap-1 font-medium">
        <FilterTypeIcon type="global" />
        <FormattedMessage id="filter.globalFilter" />
      </span>
      <span className="flex items-center gap-1 font-medium">
        <FilterTypeIcon type="tab" />
        <FormattedMessage id="filter.perTabFilter" />
      </span>
    </div>
  );
};

const Drawer = ({
  link,
  children,
  onCancel,
  onFilter,
  onOpenChange,
}: IFilterDrawer): JSX.Element => {
  return (
    <UIDrawer onOpenChange={onOpenChange}>
      <DrawerTrigger asChild>
        <ButtonWithIcon
          label={<FormattedMessage id="global.filters" />}
          icon={<IoChevronDown />}
        />
      </DrawerTrigger>

      <DrawerContent className="flex max-h-screen items-center bg-lightGray px-4">
        <DrawerHeader />
        <section className="max-h-full overflow-y-auto">
          <DrawerLink link={link} />
          <div className="w-[1000px] rounded-lg bg-white px-6">
            <div>{children}</div>
            <Legend />
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
            className="w-[200px] rounded-full bg-blue text-white"
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
