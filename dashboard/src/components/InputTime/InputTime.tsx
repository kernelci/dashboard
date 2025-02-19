import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { z } from 'zod';

import { zodResolver } from '@hookform/resolvers/zod';

import type { ControllerRenderProps, FieldError } from 'react-hook-form';
import { Controller, useForm } from 'react-hook-form';

import type { ChangeEvent, JSX } from 'react';
import { memo, useCallback } from 'react';

import { toast } from '@/hooks/useToast';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import type { PossibleMonitorPath } from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/utils/constants/general';

const TOAST_TIMEOUT = 3000;

const validateStringToNumber = (val: string): boolean => {
  const convertedNumber = parseInt(val);
  return !Number.isNaN(convertedNumber) && convertedNumber > 0;
};

const InputTime = ({
  navigateFrom,
  defaultInterval = DEFAULT_TIME_SEARCH,
}: {
  navigateFrom: PossibleMonitorPath;
  defaultInterval?: number;
}): JSX.Element => {
  const { formatMessage } = useIntl();
  const navigate = useNavigate({ from: navigateFrom });
  const { intervalInDays: interval } = useSearch({ from: navigateFrom });

  const InputTimeSchema = z.object({
    intervalInDays: z.string().refine(validateStringToNumber, {
      message: formatMessage({ id: 'filter.invalid' }),
    }),
  });

  const { handleSubmit, control } = useForm<z.infer<typeof InputTimeSchema>>({
    resolver: zodResolver(InputTimeSchema),
    defaultValues: {
      intervalInDays: `${defaultInterval}`,
    },
  });

  const onSubmit = handleSubmit(
    ({ intervalInDays }) => {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          intervalInDays: Number(intervalInDays),
        }),
      });
    },
    e => {
      const { dismiss } = toast({
        title: e.intervalInDays?.message,
        className: 'border-red bg-red text-slate-50 shadow-xl',
      });

      setTimeout(dismiss, TOAST_TIMEOUT);
    },
  );

  const onInputTimeTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (!e.target.value) {
        return;
      }
      onSubmit();
    },
    [onSubmit],
  );

  const InputTimeComponent = ({
    field: { onChange, ...rest },
    fieldError,
  }: {
    field: ControllerRenderProps<
      z.infer<typeof InputTimeSchema>,
      'intervalInDays'
    >;
    fieldError: FieldError | undefined;
  }): JSX.Element => {
    const handleInputChange = useCallback(
      (e: ChangeEvent<HTMLInputElement>) => {
        onChange(e);
        onInputTimeTextChange(e);
      },
      [onChange],
    );

    return (
      <DebounceInput
        debouncedSideEffect={handleInputChange}
        type="number"
        min={1}
        className={`${fieldError ? 'border-red' : 'border-gray'} mx-[10px] flex w-[100px] flex-1 rounded-md border`}
        startingValue={interval ? interval.toString() : `${defaultInterval}`}
        placeholder="3"
        {...rest}
      />
    );
  };

  return (
    <div className="row flex items-center text-sm">
      <FormattedMessage id="global.last" />
      <Controller
        control={control}
        name="intervalInDays"
        render={({ field, fieldState: { error: fieldError } }) => (
          <InputTimeComponent field={field} fieldError={fieldError} />
        )}
      />
      <FormattedMessage id="global.days" />
    </div>
  );
};

export const MemoizedInputTime = memo(InputTime);
