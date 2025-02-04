import { FormattedMessage, useIntl } from 'react-intl';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { z } from 'zod';

import { zodResolver } from '@hookform/resolvers/zod';

import type { ControllerRenderProps, FieldError } from 'react-hook-form';
import { Controller, useForm } from 'react-hook-form';

import type { ChangeEvent } from 'react';
import { useCallback } from 'react';

import { toast } from '@/hooks/useToast';

import { DEFAULT_TIME_SEARCH } from '@/utils/constants/general';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

export function InputTime(): JSX.Element {
  const { formatMessage } = useIntl();

  const navigate = useNavigate({ from: '/' });
  const { intervalInDays: interval } = useSearch({ from: '/tree' });

  function validateString(val: string): boolean {
    const convertedNumber = parseInt(val);
    return !Number.isNaN(convertedNumber) && convertedNumber > 0;
  }

  const InputTimeSchema = z.object({
    intervalInDays: z.string().refine(validateString, {
      message: formatMessage({ id: 'filter.invalid' }),
    }),
  });

  const { handleSubmit, control } = useForm<z.infer<typeof InputTimeSchema>>({
    resolver: zodResolver(InputTimeSchema),
    defaultValues: {
      intervalInDays: `${DEFAULT_TIME_SEARCH}`,
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

      // eslint-disable-next-line no-magic-numbers
      setTimeout(dismiss, 3000);
    },
  );

  const onInputTimeTextChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (!e.target.value) return;
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
        startingValue={
          interval ? interval.toString() : `${DEFAULT_TIME_SEARCH}`
        }
        placeholder="7"
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
}
