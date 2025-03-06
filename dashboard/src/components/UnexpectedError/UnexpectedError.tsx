import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

const UnexpectedError = (): JSX.Element => (
  <h3 className="text-weak-gray text-2xl font-semibold">
    <FormattedMessage id={'global.somethingWrong'} />
  </h3>
);

export default UnexpectedError;
