import { Outlet } from 'react-router-dom';

import SideMenu from '../../components/SideMenu/SideMenu';
import TopBar from '../../components/TopBar/TopBar';

const Root = (): JSX.Element => {
  return (
    <div className="w-full h-full">
      <div className="flex flex-row w-full justify-between">
        <SideMenu />
        <TopBar />
        <div className="w-full px-16 pt-24 bg-lightGray">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default Root;
