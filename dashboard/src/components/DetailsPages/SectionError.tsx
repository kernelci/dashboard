import { Fragment, memo, useMemo } from 'react';
import { RiProhibited2Line } from 'react-icons/ri';
import type { MessageDescriptor } from 'react-intl';
import { FormattedMessage } from 'react-intl';

interface ISectionError {
  errorMessage?: string;
  isLoading?: boolean;
  isEmpty?: boolean;
  emptyLabel?: MessageDescriptor['id'];
  customEmptyDataComponent?: JSX.Element;
}

const SectionError = ({
  errorMessage,
  isLoading,
  isEmpty,
  emptyLabel = 'global.noResults',
  customEmptyDataComponent,
}: ISectionError): JSX.Element => {
  const message = useMemo((): MessageDescriptor['id'] => {
    if (isLoading) {
      return 'global.loading';
    } else if (isEmpty) {
      return emptyLabel;
    } else if (errorMessage) {
      return 'global.error';
    }
    return 'global.error';
  }, [emptyLabel, errorMessage, isEmpty, isLoading]);

  if (isLoading === undefined) {
    return customEmptyDataComponent ?? <Fragment />;
  }

  return (
    <div className="flex flex-col items-center py-6 text-weakGray">
      {!isLoading && <RiProhibited2Line className="h-14 w-14" />}
      <p className="text-2xl font-semibold">
        <FormattedMessage id={message} />
      </p>
      {errorMessage && <p>Error: {errorMessage}</p>}
    </div>
  );
};
export const MemoizedSectionError = memo(SectionError);
