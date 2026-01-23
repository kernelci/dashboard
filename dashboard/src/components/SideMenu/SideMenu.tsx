import type { JSX } from 'react';

import SideMenuContent from './SideMenuContent';

const SideMenu = (): JSX.Element => {
  return (
    <div className="bg-bg-secondary hidden md:block">
      <SideMenuContent className="min-h-screen" />
    </div>
  );
};

export default SideMenu;
