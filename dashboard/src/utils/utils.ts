export function formatDate(date: Date | string): string {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short',
  };

  if (typeof date === 'string') date = new Date(date);
  if (isNaN(date.getTime())) return '-';

  return new Intl.DateTimeFormat('en-US', options).format(date);
}
