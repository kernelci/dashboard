import { useMemo, type JSX } from 'react';

import {
  MdOutlineCancel,
  MdOutlineCheckCircle,
  MdOutlinePending,
} from 'react-icons/md';

import { Link } from '@tanstack/react-router';

import { TiArrowSortedDown } from 'react-icons/ti';

import { useIntl } from 'react-intl';

import type { TestStatusHistoryItem } from '@/types/tree/TestDetails';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { cn } from '@/lib/utils';

export const StatusHistoryItem = ({
  historyItem,
  iconsClassName,
  isCurrentTest = false,
}: {
  historyItem: TestStatusHistoryItem;
  iconsClassName?: string;
  isCurrentTest?: boolean;
}): JSX.Element => {
  const statusIcon = useMemo(() => {
    const status = historyItem.status;
    switch (status) {
      case 'FAIL':
        return (
          <MdOutlineCancel
            className={cn(
              iconsClassName,
              'text-red text-3xl',
              !isCurrentTest && 'mt-6',
            )}
          />
        );
      case 'PASS':
        return (
          <MdOutlineCheckCircle
            className={cn(
              iconsClassName,
              'text-green text-3xl',
              !isCurrentTest && 'mt-6',
            )}
          />
        );
      default:
        return (
          <MdOutlinePending
            className={cn(
              iconsClassName,
              'text-3xl text-amber-500',
              !isCurrentTest && 'mt-6',
            )}
          />
        );
    }
  }, [historyItem.status, iconsClassName, isCurrentTest]);

  const { formatMessage } = useIntl();

  return (
    <Tooltip>
      <TooltipTrigger>
        <Link
          to="/test/$testId"
          params={{ testId: historyItem.id }}
          from="/test/$testId/"
          search={s => s}
          state={s => s}
          className="flex flex-col items-center"
        >
          {isCurrentTest && <TiArrowSortedDown className="size-6" />}
          {statusIcon}
        </Link>
      </TooltipTrigger>
      <TooltipContent>
        <p>
          {formatMessage({ id: 'global.id' }) + ': ' + historyItem.id}
          <br />
          {formatMessage({ id: 'global.status' }) + ': ' + historyItem.status}
          {historyItem.git_commit_hash && (
            <>
              <br />
              {formatMessage({ id: 'commonDetails.gitCommitHash' }) +
                ': ' +
                historyItem.git_commit_hash}
            </>
          )}
        </p>
      </TooltipContent>
    </Tooltip>
  );
};
