import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

const UnexpectedError = (): JSX.Element => (
  <h1 className="text-weak-gray text-2xl font-semibold">
    <FormattedMessage id={'global.somethingWrong'} />
  </h1>
);

export default UnexpectedError;
