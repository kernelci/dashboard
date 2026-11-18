import type { JSX } from 'react';
import { FormattedMessage, type MessageDescriptor } from 'react-intl';

export function FilterLabel({
  days,
  // The tree listing joins latest_checkout. The hardware listing sums the window.
  messageId = 'filter.latestCheckoutFilterLabel',
}: {
  days: number;
  messageId?: MessageDescriptor['id'];
}): JSX.Element {
  return (
    <p
      className="text-dim-gray text-left text-xs"
      data-test-id="listing-filter-label"
    >
      <FormattedMessage id={messageId} values={{ days }} />
    </p>
  );
}
