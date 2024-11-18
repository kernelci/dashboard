const MILLISECONDS_IN_ONE_SECOND = 1000;
const SECONDS_IN_ONE_DAY = 86400;

export const dateObjectToTimestampInSeconds = (date: Date): number => {
  return Math.floor(date.getTime() / MILLISECONDS_IN_ONE_SECOND);
};

export const daysToSeconds = (days: number): number => {
  return days * SECONDS_IN_ONE_DAY;
};
