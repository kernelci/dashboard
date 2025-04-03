const MILLISECONDS_IN_ONE_SECOND = 1000;
export const MILLISECONDS_IN_ONE_HOUR = 3600000;
const SECONDS_IN_ONE_DAY = 86400;

export const dateObjectToTimestampInSeconds = (date: Date): number => {
  return Math.floor(date.getTime() / MILLISECONDS_IN_ONE_SECOND);
};

export const daysToSeconds = (days: number): number => {
  return days * SECONDS_IN_ONE_DAY;
};

const isValidDate = (date: Date): boolean => {
  return !isNaN(date.getTime());
};

export const getFormattedDate = (
  timestampInSeconds: number,
): string | undefined => {
  const date = new Date(timestampInSeconds * MILLISECONDS_IN_ONE_SECOND);
  if (!isValidDate(date)) {
    return undefined;
  }

  const dateResult = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return dateResult;
};

export const getFormattedTime = (
  timestampInSeconds: number,
): string | undefined => {
  const date = new Date(timestampInSeconds * MILLISECONDS_IN_ONE_SECOND);
  if (!isValidDate(date)) {
    return undefined;
  }

  const timeResult = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return timeResult;
};
