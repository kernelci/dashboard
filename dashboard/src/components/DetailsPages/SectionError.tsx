import { Fragment, memo, useMemo } from 'react';
import { RiProhibited2Line } from 'react-icons/ri';
import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';

export type TErrorVariant = 'warning' | 'error';
interface ISectionError {
  errorMessage?: string;
  isLoading?: boolean;
  isEmpty?: boolean;
  emptyLabel?: MessageDescriptor['id'];
  customEmptyDataComponent?: JSX.Element;
  variant?: TErrorVariant;
}

type IErrorMessage = {
  label: string;
  id: MessageDescriptor['id'];
};

const globalErrorMessage: Record<TErrorVariant, IErrorMessage> = {
  warning: {
    label: 'Warning',
    id: 'global.warning',
  },
  error: {
    label: 'Error',
    id: 'global.error',
  },
};

const SectionError = ({
  errorMessage,
  isLoading,
  isEmpty,
  emptyLabel = 'global.noResults',
  customEmptyDataComponent,
  variant = 'error',
}: ISectionError): JSX.Element => {
  const message = useMemo((): MessageDescriptor['id'] => {
    if (isLoading) {
      return 'global.loading';
    } else if (isEmpty) {
      return emptyLabel;
    } else if (errorMessage) {
      return globalErrorMessage[variant].id;
    }
    return globalErrorMessage[variant].id;
  }, [emptyLabel, errorMessage, isEmpty, isLoading, variant]);

  if (isLoading === undefined) {
    return customEmptyDataComponent ?? <Fragment />;
  }

  return (
    <div className="flex flex-col items-center py-6 text-weakGray">
      {variant === 'error' && !isLoading && (
        <RiProhibited2Line className="h-14 w-14" />
      )}
      <p className="text-2xl font-semibold">
        <FormattedMessage id={message} />
      </p>
      {errorMessage && (
        <p>
          {globalErrorMessage[variant].label}: {errorMessage}
        </p>
      )}
    </div>
  );
};
export const MemoizedSectionError = memo(SectionError);
