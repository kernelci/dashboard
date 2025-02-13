import { useEffect, useRef, type HTMLProps, type JSX } from 'react';

import { cn } from '@/lib/utils';

export function IndeterminateCheckbox({
  indeterminate = false,
  className = '',
  ...rest
}: { indeterminate?: boolean } & HTMLProps<HTMLInputElement>): JSX.Element {
  const ref = useRef<HTMLInputElement>(null!);

  useEffect(() => {
    ref.current.indeterminate = !rest.checked && indeterminate;
  }, [ref, indeterminate, rest.checked]);

  return (
    <input
      type="checkbox"
      ref={ref}
      className={cn(className + ' cursor-pointer')}
      {...rest}
    />
  );
}
