import { format } from 'date-fns';

export function formatDate(date: Date | string, short?: boolean): string {
  const options: Intl.DateTimeFormatOptions = {
    year: short ? '2-digit' : 'numeric',
    month: short ? 'numeric' : 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: short ? undefined : 'short',
  };

  if (typeof date === 'string') date = new Date(date);
  if (isNaN(date.getTime())) return '-';

  return new Intl.DateTimeFormat('en-US', options).format(date);
}

export const getDateOffset = (date: Date): string => {
  return format(date, 'z');
};
