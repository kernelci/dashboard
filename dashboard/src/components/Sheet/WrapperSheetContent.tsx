import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage, useIntl } from 'react-intl';

import { useCallback } from 'react';

import type { ReactNode } from '@tanstack/react-router';

import {
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/Sheet';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/Tooltip/Tooltip';
import { cn } from '@/lib/utils';

export type TNavigationLogActions = {
  previousItem: () => void;
  nextItem: () => void;
  hasPrevious: boolean;
  hasNext: boolean;
  isLoading: boolean;
};

type WrapperSheetProps = {
  navigationLogsActions?: TNavigationLogActions;
  children: ReactNode;
  sheetTitle: MessageDescriptor['id'];
  detailsButton?: JSX.Element;
};

const nextItem = (
  navigationLogsActions?: WrapperSheetProps['navigationLogsActions'],
): void => {
  navigationLogsActions?.nextItem();
};

const previousItem = (
  navigationLogsActions?: WrapperSheetProps['navigationLogsActions'],
): void => {
  navigationLogsActions?.previousItem();
};

const keyboardMap: {
  [key: string]: (
    navigationLogsActions?: WrapperSheetProps['navigationLogsActions'],
  ) => void;
} = {
  ArrowRight: nextItem,
  ArrowLeft: previousItem,
  ArrowDown: nextItem,
  ArrowUp: previousItem,
  h: previousItem,
  j: nextItem,
  k: previousItem,
  l: nextItem,
};

export const WrapperSheetContent = ({
  navigationLogsActions,
  children,
  sheetTitle,
  detailsButton,
}: WrapperSheetProps): JSX.Element => {
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent): void => {
      if (!navigationLogsActions?.isLoading) {
        keyboardMap[e.key]?.(navigationLogsActions);
      }
    },
    [navigationLogsActions],
  );

  const { formatMessage } = useIntl();
  const previousTooltipMsg = `${formatMessage({ id: 'global.arrowRight' })},\
    ${formatMessage({ id: 'global.arrowUp' })}, k, h`;
  const nextTooltipMsg = `${formatMessage({ id: 'global.arrowLeft' })},\
    ${formatMessage({ id: 'global.arrowDown' })}, j, l`;

  return (
    <SheetContent
      className="flex flex-col overflow-auto sm:w-full sm:max-w-[clamp(650px,75vw,1300px)]"
      onKeyDown={handleKeyDown}
    >
      <SheetHeader className="mb-3">
        <SheetTitle className="text-[1.75rem]">
          <FormattedMessage id={sheetTitle} />
        </SheetTitle>
      </SheetHeader>

      {children}

      <div
        className={cn(
          'mt-auto flex',
          detailsButton ? 'justify-between' : 'justify-end',
        )}
      >
        {detailsButton}
        <div className="flex">
          <div className="mt-auto flex justify-end">
            {navigationLogsActions && (
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      onClick={navigationLogsActions.previousItem}
                      disabled={!navigationLogsActions.hasPrevious}
                      className="rounded-3xl bg-[#11B3E6] px-14 font-bold text-white"
                    >
                      <FormattedMessage
                        id="global.prev"
                        defaultMessage="Previous"
                      />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>{previousTooltipMsg}</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      onClick={navigationLogsActions.nextItem}
                      disabled={!navigationLogsActions.hasNext}
                      className="mx-5 rounded-3xl bg-[#11B3E6] px-14 font-bold text-white"
                    >
                      <FormattedMessage
                        id="global.next"
                        defaultMessage="Next"
                      />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>{nextTooltipMsg}</TooltipContent>
                </Tooltip>
              </>
            )}
          </div>
          <SheetTrigger asChild>
            <Button className="rounded-3xl bg-[#11B3E6] px-14 font-bold text-white">
              <FormattedMessage id="global.close" defaultMessage="Close" />
            </Button>
          </SheetTrigger>
        </div>
      </div>
    </SheetContent>
  );
};
