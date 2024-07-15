import { FormattedMessage } from 'react-intl';

const TopBar = (): JSX.Element => {
  return (
    <div className="flex fixed top-0 h-20 mx-52 pl-6 pr-12 bg-white w-full">
      <div className="flex flex-row w-full items-center justify-between">
        <span className="text-2xl ">
          <FormattedMessage id="routes.treeMonitor" />
        </span>
      </div>
    </div>
  );
};

export default TopBar;
