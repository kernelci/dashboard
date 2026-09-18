import type { ButtonHTMLAttributes, JSX } from 'react';

import { cn } from '@/lib/utils';

interface IFilterButton extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected: boolean;
}

export const FilterButton = ({
  selected,
  className,
  ...props
}: IFilterButton): JSX.Element => (
  <button
    type="button"
    aria-pressed={selected}
    className={cn(
      'focus-visible:ring-blue h-9 rounded-full border px-3 text-sm font-medium transition duration-150 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none',
      selected
        ? 'bg-blue hover:bg-blue border-[#0d9ac8] text-white shadow-[0_2px_4px_rgba(0,0,0,0.2)] hover:text-white'
        : 'border-dark-gray bg-light-gray text-dim-gray hover:text-dim-black shadow-none',
      className,
    )}
    {...props}
  />
);
