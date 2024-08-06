import { FormattedMessage } from 'react-intl';

const UnexpectedError = (): JSX.Element => (
  <h1 className="text-2xl font-semibold text-weakGray">
    <FormattedMessage id={'global.somethingWrong'} />
  </h1>
);

export default UnexpectedError;
