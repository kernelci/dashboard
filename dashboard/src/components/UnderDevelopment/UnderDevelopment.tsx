import { FormattedMessage } from 'react-intl';

export const UnderDevelopment = (): JSX.Element => {
  return (
    <div className="grid h-[400px] place-items-center rounded-md bg-slate-100 dark:bg-slate-800">
      <FormattedMessage id="global.underDevelopment" />
    </div>
  );
};
