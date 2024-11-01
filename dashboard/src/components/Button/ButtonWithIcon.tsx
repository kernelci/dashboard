import type { ReactElement } from 'react';

import { cn } from '@/lib/utils';

import { Button } from '../ui/button';

interface IButtonWithIcon extends React.ComponentProps<typeof Button> {
  icon?: ReactElement;
  label?: ReactElement;
  className?: string;
}

const buttonsClassName =
  'bg-lightGray border-2 border-black text-black rounded-full items-center gap-2 hover:bg-darkGray px-6';

const ButtonWithIcon = ({
  icon,
  label,
  className,
  ...props
}: IButtonWithIcon): JSX.Element => {
  return (
    <Button className={cn(buttonsClassName, className)} {...props}>
      {label}
      {icon}
    </Button>
  );
};

export default ButtonWithIcon;
