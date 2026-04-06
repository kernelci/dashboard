import {
  memo,
  useCallback,
  useEffect,
  useRef,
  useState,
  type JSX,
} from 'react';

import { useNavigate, useSearch } from '@tanstack/react-router';

import type { MessageDescriptor } from 'react-intl';
import { useIntl } from 'react-intl';

import { Input } from '@/components/ui/input';
import {
  dateObjectToTimestampInSeconds,
  daysToSeconds,
  MILLISECONDS_IN_ONE_SECOND,
} from '@/utils/date';
import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';
import { cn } from '@/lib/utils';

const ERROR_CLEAR_TIMEOUT = 3000;
const ISO_DATE_LENGTH = 10;
const MIN_DATE_STR = '2024-01-01';

const getDefaultEndTimestamp = (): number =>
  dateObjectToTimestampInSeconds(new Date());

const getDefaultStartTimestamp = (): number =>
  getDefaultEndTimestamp() - daysToSeconds(REDUCED_TIME_SEARCH);

const timestampToDateString = (ts: number): string =>
  new Date(ts * MILLISECONDS_IN_ONE_SECOND)
    .toISOString()
    .slice(0, ISO_DATE_LENGTH);

const dateStringToTimestamp = (dateStr: string): number =>
  Math.floor(new Date(dateStr).getTime() / MILLISECONDS_IN_ONE_SECOND);

type ErrorField = 'start' | 'startTooEarly' | 'end' | 'endFuture' | null;

const DateRangeInput = (): JSX.Element => {
  const { formatMessage } = useIntl();
  const navigate = useNavigate({ from: '/issues' });
  const { startTimestampInSeconds, endTimestampInSeconds } = useSearch({
    from: '/_main/issues',
  });

  const todayTs = getDefaultEndTimestamp();
  const startTs = startTimestampInSeconds ?? getDefaultStartTimestamp();
  const endTs = endTimestampInSeconds ?? todayTs;

  const todayDateStr = timestampToDateString(todayTs);

  const startDateStr = timestampToDateString(startTs);
  const endDateStr = timestampToDateString(endTs);

  const [errorField, setErrorField] = useState<ErrorField>(null);
  const clearErrorRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const triggerError = useCallback((field: ErrorField): void => {
    if (clearErrorRef.current) {
      clearTimeout(clearErrorRef.current);
    }
    setErrorField(field);
    clearErrorRef.current = setTimeout(
      () => setErrorField(null),
      ERROR_CLEAR_TIMEOUT,
    );
  }, []);

  useEffect((): (() => void) => {
    return () => {
      if (clearErrorRef.current) {
        clearTimeout(clearErrorRef.current);
      }
    };
  }, []);

  const handleStartChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.value) {
        return;
      }
      const newStartTs = dateStringToTimestamp(e.target.value);
      if (newStartTs < dateStringToTimestamp(MIN_DATE_STR)) {
        triggerError('startTooEarly');
        return;
      }
      if (newStartTs > endTs) {
        triggerError('start');
        return;
      }
      setErrorField(null);
      navigate({
        search: prev => ({ ...prev, startTimestampInSeconds: newStartTs }),
      });
    },
    [navigate, endTs, triggerError],
  );

  const handleEndChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.value) {
        return;
      }
      const newEndTs = dateStringToTimestamp(e.target.value);
      if (newEndTs > todayTs) {
        triggerError('endFuture');
        return;
      }
      if (newEndTs < startTs) {
        triggerError('end');
        return;
      }
      setErrorField(null);
      navigate({
        search: prev => ({ ...prev, endTimestampInSeconds: newEndTs }),
      });
    },
    [navigate, startTs, todayTs, triggerError],
  );

  const errorMessageIds: Record<
    NonNullable<ErrorField>,
    MessageDescriptor['id']
  > = {
    start: 'dateRange.startAfterEnd',
    startTooEarly: 'dateRange.startTooEarly',
    end: 'dateRange.endBeforeStart',
    endFuture: 'dateRange.endAfterToday',
  };

  const errorMessageId = errorField ? errorMessageIds[errorField] : null;
  const errorMessage = errorMessageId
    ? formatMessage({ id: errorMessageId })
    : null;

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex items-center gap-2 text-sm">
        <Input
          type="date"
          value={startDateStr}
          min={MIN_DATE_STR}
          max={endDateStr}
          onChange={handleStartChange}
          className={cn(
            'w-[140px] cursor-pointer',
            errorField === 'start' ? 'border-red' : '',
          )}
          data-test-id="date-range-start"
        />
        <span className="text-dim-gray">–</span>
        <Input
          type="date"
          value={endDateStr}
          min={startDateStr}
          max={todayDateStr}
          onChange={handleEndChange}
          className={cn(
            'w-[140px] cursor-pointer',
            errorField === 'start' ? 'border-red' : '',
          )}
          data-test-id="date-range-end"
        />
      </div>
      {errorMessage && <span className="text-red text-sm">{errorMessage}</span>}
    </div>
  );
};

export const MemoizedDateRangeInput = memo(DateRangeInput);
