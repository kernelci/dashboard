import { LiaInfoCircleSolid } from 'react-icons/lia';
import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

export const DETAILS_COLUMN_ID = 'details';

export const MoreDetailsIcon = (): JSX.Element => (
  <LiaInfoCircleSolid className="h-5 w-5" />
);

export const MoreDetailsTableHeader = (): JSX.Element => (
  <span className="font-medium">
    <FormattedMessage
      id="global.details"
      key={'global.details'}
      defaultMessage={'Details'}
    />
  </span>
);
