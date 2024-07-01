import { FormattedMessage } from "react-intl";

import { Input } from "../ui/input";

const TopBar = (): JSX.Element => {
  return (
    <div className="flex fixed top-0 h-20 mx-52 pl-6 pr-12 bg-white w-full">
      <div className="flex flex-row w-full items-center justify-between">
        <span className="text-2xl ">
          <FormattedMessage id="routes.treeMonitor" />
        </span>
        <div className="flex w-2/3 px-6 items-center">
          {/* placeholder for search */}
          {/* TODO: use i18n for the input placeholder */}
          <Input className="w-2/3" type="text" placeholder="Search by tree, branch or tag" />
        </div>
      </div>
    </div>
  );
};

export default TopBar;
