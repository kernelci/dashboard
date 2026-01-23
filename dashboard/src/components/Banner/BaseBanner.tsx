import type { VariantProps } from 'class-variance-authority';
import { cva } from 'class-variance-authority';
import type { JSX } from 'react';

import { cn } from '@/lib/utils';

const bannerVariants = cva('rounded-md p-3 text-sm', {
  variants: {
    variant: {
      default:
        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      green:
        'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
});

export const BaseBanner = ({
  children,
  variant,
  className,
}: {
  children: JSX.Element;
  variant?: VariantProps<typeof bannerVariants>['variant'];
  className?: string;
}): JSX.Element => {
  return (
    <div className={cn(bannerVariants({ variant }), className)}>{children}</div>
  );
};
