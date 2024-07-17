import { useState, useEffect } from 'react';

export const useDebounce = <T,>(input: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState(input);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(input);
    }, delay);
    return (): void => {
      clearTimeout(handler);
    };
  }, [input, delay]);

  return debouncedValue;
};
