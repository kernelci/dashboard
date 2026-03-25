import type { JSX } from 'react';

import SideMenuContent from './SideMenuContent';

const SideMenu = (): JSX.Element => {
  return (
    <div className="bg-bg-secondary sticky top-0 hidden h-screen overflow-y-auto md:block">
      <SideMenuContent className="min-h-screen" />
    </div>
  );
};

export default SideMenu;
