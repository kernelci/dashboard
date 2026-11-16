import { type JSX, memo } from 'react';

import { Link, type LinkProps } from '@tanstack/react-router';

import { cn } from '@/lib/utils';

const LinkItem = ({
  children,
  className,
  ...props
}: LinkProps & { className?: string }): JSX.Element => {
  return (
    <Link
      {...props}
      className={cn(
        'flex flex-row items-center gap-1 underline hover:text-slate-900',
        className,
      )}
      target="_blank"
      rel="noreferrer"
    >
      {children}
    </Link>
  );
};

export default memo(LinkItem);
