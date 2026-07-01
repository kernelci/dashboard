import type { JSX } from 'react';
import { FormattedMessage } from 'react-intl';

export function FilterLabel({ days }: { days: number }): JSX.Element {
  return (
    <p
      className="text-dim-gray text-left text-xs"
      data-test-id="hardware-filter-label"
    >
      <FormattedMessage
        id="hardwareListing.latestCheckoutFilterLabel"
        values={{ days }}
      />
    </p>
  );
}
