import { useMemo, type JSX } from 'react';

import {
  MdOutlineCancel,
  MdOutlineCheckCircle,
  MdOutlinePending,
} from 'react-icons/md';

import { Link } from '@tanstack/react-router';

import type { TestStatusHistoryItem } from '@/types/tree/TestDetails';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { cn } from '@/lib/utils';

export const StatusHistoryItem = ({
  historyItem,
  iconsClassName,
}: {
  historyItem: TestStatusHistoryItem;
  iconsClassName?: string;
}): JSX.Element => {
  const statusIcon = useMemo(() => {
    const status = historyItem.status;
    switch (status) {
      case 'FAIL':
        return (
          <MdOutlineCancel
            className={cn(iconsClassName, 'text-red text-2xl')}
          />
        );
      case 'PASS':
        return (
          <MdOutlineCheckCircle
            className={cn(iconsClassName, 'text-green text-2xl')}
          />
        );
      default:
        return (
          <MdOutlinePending
            className={cn(iconsClassName, 'text-2xl text-amber-500')}
          />
        );
    }
  }, [historyItem.status, iconsClassName]);

  return (
    <Tooltip>
      <TooltipTrigger>
        <Link
          to="/test/$testId"
          params={{ testId: historyItem.id }}
          from="/test/$testId/"
          search={s => s}
          state={s => s}
        >
          {statusIcon}
        </Link>
      </TooltipTrigger>
      <TooltipContent>{historyItem.id}</TooltipContent>
    </Tooltip>
  );
};
