import { match, P } from 'ts-pattern';

import { MdCheck, MdClose, MdOutlinePending } from 'react-icons/md';

import type { JSX } from 'react';

import { cn } from '@/lib/utils';

import type { Status } from '@/types/database';

const commonClass = 'text-2xl';

export const StatusIcon = ({
  className,
  status,
  showText = false,
}: {
  className?: string;
  status?: Status | boolean;
  showText?: boolean;
}): JSX.Element => {
  const { color, icon } = match(status)
    .with(P.union('PASS', true), _ => {
      return {
        color: 'text-green',
        icon: <MdCheck className={cn(commonClass, className, 'text-green')} />,
      };
    })
    .with(P.union('FAIL', false), _ => {
      return {
        color: 'text-red',
        icon: <MdClose className={cn(commonClass, className, 'text-red')} />,
      };
    })
    .otherwise(_ => {
      return {
        color: 'text-amber-500',
        icon: (
          <MdOutlinePending
            className={cn(commonClass, className, 'text-amber-500')}
          />
        ),
      };
    });

  if (showText) {
    return (
      <div className="flex items-center gap-1">
        <p className={cn('text-2xl font-bold', color)}>{status}</p>
        {icon}
      </div>
    );
  }

  return icon;
};
