import { useState, useEffect } from 'react';

export const useDebounce = (input: string, delay: number): string => {
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
