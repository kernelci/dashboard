import { useState, useEffect, useCallback } from 'react';

export const usePagination = (
  totalItems: number,
  itemsPerPage: number,
): {
  startIndex: number;
  endIndex: number;
  onClickGoForward: () => void;
  onClickGoBack: () => void;
} => {
  const [startIndex, setStartIndex] = useState(0);
  const [endIndex, setEndIndex] = useState(0);

  useEffect(() => {
    setEndIndex(totalItems > itemsPerPage ? itemsPerPage : totalItems);
  }, [itemsPerPage, totalItems]);

  const onClickGoForward = useCallback(() => {
    setStartIndex(endIndex);
    setEndIndex(
      endIndex + itemsPerPage >= totalItems
        ? totalItems
        : endIndex + itemsPerPage,
    );
  }, [endIndex, itemsPerPage, totalItems]);

  const onClickGoBack = useCallback(() => {
    setStartIndex(startIndex - itemsPerPage);
    setEndIndex(
      endIndex % itemsPerPage !== 0
        ? endIndex - (endIndex % itemsPerPage)
        : endIndex - itemsPerPage,
    );
  }, [startIndex, itemsPerPage, endIndex]);

  return { startIndex, endIndex, onClickGoForward, onClickGoBack };
};
