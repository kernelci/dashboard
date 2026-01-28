import React, { useMemo, type JSX } from 'react';
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
  title: MessageDescriptor['id'];
  value: string;
  url?: string;
}

interface IFilterDrawer {
  onOpenChange?: (open: boolean) => void;
  children?: React.ReactNode;
  onCancel?: () => void;
  onFilter?: () => void;
  showLegend?: boolean;
  link?: IDrawerLink;
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

const DrawerLink = ({ title, value, url }: IDrawerLink): JSX.Element => {
  return (
    <div className="mb-8 flex items-center justify-between">
      <div className="border-dark-gray flex h-[52px] w-full flex-col border bg-white px-4 py-2">
        <span className="text-dark-gray2 text-xs">
          <FormattedMessage id={title} />
        </span>
        <a
          className="text-dim-black text-base underline"
          href={url ?? '#'}
          target={url ? '_blank' : undefined}
          rel="noreferrer"
        >
          {value}
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
      <div className="not-first:pt-10 not-last:pb-10">{children}</div>
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
    <div className="flex items-center gap-1 pb-10">
      <span className="mr-1 font-semibold">
        <FormattedMessage id="global.legend" />
      </span>
      <span className="flex items-center gap-1">
        <FilterTypeIcon type="global" />
        <FormattedMessage id="filter.globalFilter" />
      </span>
      <span className="flex items-center gap-1">
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
  showLegend = true,
}: IFilterDrawer): JSX.Element => {
  const drawerLinkComponent = useMemo(() => {
    if (link) {
      return (
        <DrawerLink title={link.title} value={link.value} url={link.url} />
      );
    }
    return <></>;
  }, [link]);

  return (
    <UIDrawer onOpenChange={onOpenChange}>
      <DrawerTrigger asChild>
        <ButtonWithIcon
          label={<FormattedMessage id="global.filters" />}
          icon={<IoChevronDown />}
        />
      </DrawerTrigger>

      <DrawerContent className="bg-light-gray flex h-screen items-center px-4">
        <DrawerHeader />
        <section className="h-full overflow-y-auto">
          {drawerLinkComponent}
          <div className="w-[1000px] rounded-lg bg-white px-6 py-5">
            {showLegend && <Legend />}
            <div>{children}</div>
          </div>
        </section>

        <DrawerFooter className="text-dim-gray mt-6 flex h-20 w-full flex-row justify-end gap-x-6 bg-white">
          <DrawerClose asChild>
            <Button
              variant="ghost"
              onClick={onCancel}
              data-test-id="filter-cancel-button"
            >
              <FormattedMessage id={'global.cancel'} />
            </Button>
          </DrawerClose>
          <DrawerClose
            asChild
            className="bg-blue w-[200px] rounded-full text-white"
          >
            <Button
              variant="outline"
              onClick={onFilter}
              data-test-id="filter-button"
            >
              <FormattedMessage id="global.filter" />
            </Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </UIDrawer>
  );
};

export default Drawer;
