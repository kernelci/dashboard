import { FormattedMessage } from 'react-intl';

const UnexpectedError = (): JSX.Element => (
  <h1 className="font-semibold text-2xl text-weakGray">
    <FormattedMessage id={'global.somethingWrong'} />
  </h1>
);

export default UnexpectedError;
