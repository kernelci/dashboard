import { differenceInDays } from 'date-fns';

const RELATIVE_DAYS_EDGE = 3;

export const shouldShowRelativeDate = (
  date: string,
  limitInDays: number = RELATIVE_DAYS_EDGE,
): boolean => {
  const treeDate = new Date(date);
  const currentDate = new Date();
  const days = differenceInDays(currentDate, treeDate);

  return days < limitInDays;
};
