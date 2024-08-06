import { Outlet } from 'react-router-dom';

import SideMenu from '../../components/SideMenu/SideMenu';
import TopBar from '../../components/TopBar/TopBar';

const Root = (): JSX.Element => {
  return (
    <div className="h-full w-full">
      <div className="flex w-full flex-row justify-between">
        <SideMenu />
        <TopBar />
        <div className="w-full bg-lightGray px-16 pt-24">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default Root;
