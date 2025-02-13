import { match, P } from 'ts-pattern';

import { MdCheck, MdClose, MdOutlinePending } from 'react-icons/md';

import type { JSX } from 'react';

import { cn } from '@/lib/utils';

import type { Status } from '@/types/database';

const commonClass = 'text-2xl';

export const StatusIcon = ({
  className,
  status,
}: {
  className?: string;
  status?: Status | boolean;
}): JSX.Element => {
  return match(status)
    .with(P.union('PASS', true), _ => (
      <MdCheck className={cn(commonClass, className, 'text-green')} />
    ))
    .with(P.union('FAIL', false), _ => (
      <MdClose className={cn(commonClass, className, 'text-red')} />
    ))
    .otherwise(_ => (
      <MdOutlinePending
        className={cn(commonClass, className, 'text-amber-500')}
      />
    ));
};
