import type { ChangeEvent, JSX } from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';

import { useDebounce } from '@/hooks/useDebounce';
import type { InputProps } from '@/components/ui/input';
import { Input } from '@/components/ui/input';

interface IDebounceInput extends Omit<InputProps, 'onChange' | 'value'> {
  debouncedSideEffect: (value: ChangeEvent<HTMLInputElement>) => void;
  startingValue?: string;
}

const DEBOUNCE_INTERVAL = 500;

const DebounceInput = ({
  debouncedSideEffect,
  startingValue = '',
  ...props
}: IDebounceInput): JSX.Element => {
  const [inputValue, setInputValue] = useState<string>(startingValue);
  const [inputEvent, setInputEvent] = useState<ChangeEvent<HTMLInputElement>>();
  const isThisComponentMounted = useRef(true);
  const lastProcessedValue = useRef<string>(startingValue);
  const debouncedInputEvent = useDebounce(inputEvent, DEBOUNCE_INTERVAL);

  useEffect(() => {
    setInputValue(startingValue);
    lastProcessedValue.current = startingValue;
  }, [startingValue]);

  const onInputSearchTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>): void => {
      setInputValue(e.target.value);
      setInputEvent(e);
    },
    [],
  );

  useEffect(() => {
    isThisComponentMounted.current = true;

    if (
      debouncedInputEvent &&
      isThisComponentMounted.current &&
      debouncedInputEvent.target.value !== lastProcessedValue.current
    ) {
      debouncedSideEffect(debouncedInputEvent);
      lastProcessedValue.current = debouncedInputEvent.target.value;
    }

    return (): void => {
      isThisComponentMounted.current = false;
    };
  }, [debouncedInputEvent, debouncedSideEffect, lastProcessedValue]);

  return (
    <Input {...props} onChange={onInputSearchTextChange} value={inputValue} />
  );
};

export default DebounceInput;
