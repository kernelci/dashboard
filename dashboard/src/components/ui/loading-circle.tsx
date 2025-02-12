import * as React from 'react';

import { cn } from '@/lib/utils';

export const LoadingCircle = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      className,
      'text-surface text-blue inline-block h-6 w-6 animate-spin rounded-full border-[3px] border-solid border-x-current border-y-current border-e-transparent motion-reduce:animate-[spin_1.5s_linear_infinite]',
    )}
    role="status"
    {...props}
  />
);
