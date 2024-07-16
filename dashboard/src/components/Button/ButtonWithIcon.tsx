import { ReactElement } from 'react';
import classNames from 'classnames';

import { Button } from '../ui/button';

interface IButtonWithIcon {
  icon?: ReactElement;
  label?: ReactElement;
  className?: string;
}

const buttonsClassName =
  'bg-lightGray border border-black text-black rounded-full items-center gap-2 hover:bg-darkGray px-6';

const ButtonWithIcon = ({
  icon,
  label,
  className,
}: IButtonWithIcon): JSX.Element => {
  return (
    <Button className={classNames(buttonsClassName, className)}>
      {label}
      {icon}
    </Button>
  );
};

export default ButtonWithIcon;
