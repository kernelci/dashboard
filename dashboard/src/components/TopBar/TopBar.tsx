import { FormattedMessage } from 'react-intl';

const TopBar = (): JSX.Element => {
  return (
    <div className="fixed top-0 z-10 mx-52 flex h-20 w-full bg-white px-16">
      <div className="flex w-full flex-row items-center justify-between">
        <span className="text-2xl">
          <FormattedMessage id="routes.treeMonitor" />
        </span>
      </div>
    </div>
  );
};

export default TopBar;
