import { useEffect, useRef, type HTMLProps, type JSX } from 'react';

export function IndeterminateCheckbox({
  indeterminate = false,
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
      className="size-4 cursor-pointer"
      {...rest}
    />
  );
}
