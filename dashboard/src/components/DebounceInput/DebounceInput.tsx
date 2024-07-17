import { useEffect, useState } from 'react';

import { useDebounce } from '../../hooks/useDebounce';
import { Input, InputProps } from '../ui/input';

interface IDebounceInput extends InputProps {
  interval: number;
}

const DebounceInput = ({
  interval,
  onChange,
  ...props
}: IDebounceInput): JSX.Element => {
  const [inputEvent, setInputEvent] =
    useState<React.ChangeEvent<HTMLInputElement>>();
  const eDebounced = useDebounce(inputEvent, interval);

  const onInputSearchTextChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ): void => {
    setInputEvent(e);
  };

  useEffect(() => {
    if (eDebounced && onChange) onChange(eDebounced);
  }, [eDebounced, onChange]);

  return <Input {...props} onChange={onInputSearchTextChange} />;
};

export default DebounceInput;
