import type { ButtonHTMLAttributes, JSX } from 'react';

import { cn } from '@/lib/utils';

export const PillButton = ({
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>): JSX.Element => (
  <button
    type="button"
    className={cn(
      'focus-visible:ring-blue border-dark-gray bg-light-gray text-dim-gray hover:text-dim-black h-9 rounded-full border px-3 text-sm font-medium transition duration-150 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none',
      className,
    )}
    {...props}
  />
);

interface IFilterButton extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected: boolean;
}

export const FilterButton = ({
  selected,
  className,
  ...props
}: IFilterButton): JSX.Element => (
  <PillButton
    aria-pressed={selected}
    className={cn(
      selected &&
        'bg-blue hover:bg-blue border-blue text-white shadow-[0_2px_4px_rgba(0,0,0,0.2)] hover:text-white',
      className,
    )}
    {...props}
  />
);
