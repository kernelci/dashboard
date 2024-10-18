import { ChangeEvent, useEffect, useRef, useState } from 'react';

import { useDebounce } from '@/hooks/useDebounce';
import { Input, InputProps } from '@/components/ui/input';

interface IDebounceInput extends Omit<InputProps, 'value'> {
  debouncedInterval: number;
  debouncedSideEffect: (value: React.ChangeEvent<HTMLInputElement>) => void;
  startingValue?: string;
}

const DebounceInput = ({
  debouncedInterval,
  debouncedSideEffect,
  startingValue = '',
  ...props
}: IDebounceInput): JSX.Element => {
  const [inputValue, setInputValue] = useState<string>(startingValue);
  const [inputEvent, setInputEvent] = useState<ChangeEvent<HTMLInputElement>>();
  const isThisComponentMounted = useRef(true);
  const debouncedInputEvent = useDebounce(inputEvent, debouncedInterval);

  const onInputSearchTextChange = (e: ChangeEvent<HTMLInputElement>): void => {
    setInputValue(e.target.value);
    setInputEvent(e);
  };

  useEffect(() => {
    //For double rendering
    isThisComponentMounted.current = true;

    if (debouncedInputEvent && isThisComponentMounted.current) {
      debouncedSideEffect(debouncedInputEvent);
    }
    return (): void => {
      //Prevents from being called in another page after the input is no longer relevant
      isThisComponentMounted.current = false;
    };
  }, [debouncedInputEvent, debouncedSideEffect]);

  return (
    <Input {...props} onChange={onInputSearchTextChange} value={inputValue} />
  );
};

export default DebounceInput;
